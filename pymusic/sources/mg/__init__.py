from urllib.parse import quote
from random import choice
from hashlib import sha1
import asyncio
import json

from aiohttp import ClientSession
from lxml.html import fromstring
from re import compile

from pymusic.lib import aiofile
from pymusic.lib.RSA import RSA
from pymusic.lib.AES import encrypt
from ..model import SongInfo
from ..model import SourceModel


class Source(SourceModel):
    """咪咕."""

    SEARCH_URL = 'https://music.migu.cn/v3/search'
    SOURCE_URL = 'https://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo'
    LOGIN_URL = 'https://passport.migu.cn/authn'
    LOGIN_CALLBACK_URL = 'https://music.migu.cn/v3/user/login'
    PUBLICKEY_URL = 'https://passport.migu.cn/password/publickey'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self.__parser = aiofile.AWrapper(fromstring)
        self.__app_info = self._loop.create_task(self.__init_migu_app())
        self.__publickey = self._loop.create_task(self.__init_publickey())

    async def _init_cookies(self) -> None:
        self.__init_migu_cookie_id()

    async def __init_migu_app(self):
        """初始化咪咕参数."""

        sess: ClientSession = await self._sess
        url = 'https://music.migu.cn/v3'
        res = await sess.get(url)
        source_page = await res.text()
        tree = await self.__parser(source_page)
        app_info = tree.xpath('//script[@type="text/javascript"]/text()')[0]
        app_info = compile(r'{([\s\S]+?)}').search(app_info).group(1)
        return {
            k.strip(): v.strip().strip("'").strip('"')
            for k, v in [
                pair.split(':', 1)
                for pair in app_info.split(',\n')
                if pair
            ]
        }

    def __init_migu_cookie_id(self) -> None:
        """初始化mg_cookie_id."""

        def get_uuid():
            s = list('0123456789abcdef')
            t = [choice(s) for _ in range(36)]
            t[14] = "4"
            try:
                tt = int(t[19])
            except ValueError:
                tt = 0
            t[19] = s[3 & tt | 8]
            t[8] = t[13] = t[18] = t[23] = '-'
            return ''.join(t)

        self._cookies['migu_cookie_id'] = \
            get_uuid() + '-n4' + str(self._get_time_stamp(13))

    async def __init_publickey(self):
        """初始化公钥."""

        sess: ClientSession = await self._sess
        res = await sess.post(self.PUBLICKEY_URL)
        res = await res.json(content_type=None)
        if res['status'] != 2000:
            raise RuntimeError('get publickey error: ' + res['message'])
        return res['result']

    def __encrypt(self, params: dict, source_id: str) -> str:
        """加密获取i参数."""

        params = params.copy()
        params['keyword'] = quote(params['keyword'])
        params['u'] = self._headers['user-agent'] + '/' + source_id
        params['k'] = self._cookies['migu_cookie_id']
        key_str = ''.join(k + str(params[k]) for k in sorted(params))
        key_str = quote(key_str, safe='()')
        return sha1(key_str.encode()).hexdigest()

    def __parse_data(self, data: list) -> list:
        """解析页面数据."""

        def parse(tree) -> SongInfo:
            info = tree.xpath(
                './div[@class="song-actions single-column"]//@data-share',
            )[0]
            info_dict = json.loads(info)
            summary = [info_dict['title'], info_dict['singer']]
            if info_dict.get('album') is not None:
                summary.append(info_dict['album'])
            source_id = info_dict['linkUrl'].split('/')[-1]
            return SongInfo(
                summary=' -> '.join(summary),
                id_=source_id,
                type_='mp3',
                from_='mg',
            )

        return [parse(tree) for tree in data]

    async def _get_info(self, name: str) -> SongInfo:
        sess: ClientSession = await self._sess
        sess.headers['referer'] = 'https://music.migu.cn/v3'
        time_stamp = self._get_time_stamp()
        app_info = await self.__app_info
        params = {
            "f": "html",
            "s": time_stamp,
            "c": app_info['CHANNEL_ID'],
            "keyword": name,
            "v": app_info['APP_VERSION'],
        }
        i = self.__encrypt(params, (await self.__app_info)['SOURCE_ID'])
        params.update({
            'i': i,
            'page': 1,
            'type': 'song',
        })
        res = await sess.get(self.SEARCH_URL, params=params)
        res_text = await res.text()
        tree = await self.__parser(res_text)
        data = tree.xpath('//div[@class="songlist-body"]/div')
        return self.__parse_data(data)

    async def _get_source(self, source_id: str) -> str:
        sess: ClientSession = await self._sess
        sess.headers['referer'] = 'https://music.migu.cn/v3/music/player/audio'
        key = \
            '4ea5c508a6566e76240543f8feb06fd457777be39549c4016436afda65d2330e'
        data = {
            'copyrightId': source_id,
            'type': 2,
            "auditionsFlag": 11,
        }
        data = json.dumps(data).replace(' ', '')
        data = encrypt(data, key).decode()
        params = {
            'dataType': 2,
            'data': data,
            'secKey':
            'kHJ2i6869DhR3vATP9q1bBGWyL4gPbSQDMUMM/pHQpWr721h4K6UnptCgioY23Xcc'
            'BjCWdQepKlOV55c8aEL9VM0M47PBqSgrqR/rksGCpY4VukRY5bZjBMXeV7l78eErH'
            '9c4wh5x2BG4Y7PiW15Xod2DTQIziD2IYDly+RSI9U='
        }
        res = await sess.get(
            self.SOURCE_URL,
            params=params,
            allow_redirects=False,
        )
        res = await res.json(content_type=None)
        # N000000 未登录
        # N000001 参数不合法
        status_code = res['returnCode']
        if status_code != '000000':
            if status_code == 'N000000':
                return -1
            else:
                raise RuntimeError('get source error:' + res['msg'])
        url = res['data']['playUrl']
        if url:
            return 'https:' + url

    async def __login_by_password(
        self,
        login_id: str,
        password: str,
        *args,
    ) -> int:
        sess: ClientSession = await self._sess
        app_info = await self.__app_info
        publickey = await self.__publickey
        n, e = publickey['modulus'], publickey['publicExponent']
        rsa = RSA(n, e)
        data = {
            'sourceID': app_info['SOURCE_ID'],
            'appType': '0',
            'relayState': '',
            'loginID': rsa.encrypt(login_id),
            'enpassword': rsa.encrypt(password),
            'captcha': '',
            'imgcodeType': '1',
            'rememberMeBox': '1',
            'fingerPrint':
            '365f397d7a702e0ba61a0c81be7447500c0568561479bcb3da6ba896070cc336f'
            '6e8e3d5051a38a243ac8cfc57c642c897e04785ab7e2fbc9c674322cd697a3e70'
            '389cf3b5ae23e117294f895975aece81c93854dd97025f55cab44a5ef54a35cc0'
            '561354a8755a35d0ba0d625b8fab4c4cd8581009ae0c9570fb29ee715fed3',
            'fingerPrintDetail': '1f33883710fa9e30f6ecdb2324fcfea43a542590751fc54a08f094ceb440f5d680327edbf709f48390419d796628e32d5d8c44d4e79d6087d3963c71b260033023de27504d17d1e4c7fb925ee5ce4224569c5073e050462947781d2c57f551480ff194984fda31651a82c75d12cd72776f950a9aea82c8e5bc03744929f53864644ea8109ffdf2284db2a7799537ff50f8c0b9f160ddf45582a12c4fd500cd07c6d4eded3120f73ba57e5cb59986463c992d1ffe89df8307be6bd532a5842bedcaaf9138b905e28bc9f2e9a17e58a6e2f954e46f48cb5a86a77470c11c3520213879df9da08e243c5a1ab96d809b272d9c47682a5297eed2c6efff7dc4c042796909771a6baa300b7bb652901be5a399f6a5193ba54fcf1e9d227431539df077b1b97afe235007fd777b4e21b22bdfb231190747296d704d0070e5e818195f50f81734a7b34376fc314ec14a3530830354f1b261112c21ac9f53be126b6a5e68b9568e584fed59a71c7c859c7be6a4cf4464942bd9abf6efb8ca1922140204051621c2588c7a7824996401a2fc40a1416683e40874fa6172471146329c19db6ee497a0134d415189d8d67e9e41b8a0ab7d1de8547de01e824fb64e72acb13a4d954177bddac21ec5b0442c12e501cb42c50904aaec011e36b283b046a6d57576f9069940c4d6cfe51ddbd88e0e5628b25a954e2a57a3cdaedede781724b2f6d551ae34933c11033b1dffa5bc9cc5d52e6b1eb07ad85968298c0a87264c0d174dea088ae3cff2f79c9ab80e6b508d1bb25175195387715b9c87a2e5d0267ef85f2fdc5d845a21f800453da1b826ad588fb8eaa3927f8f9fde13f4994f8a4d83743ce2cbf766b3785cce8b7e33d75b77e4d54d1c0d1baeb3dcf342911d5224e60b2ee90423bd9b190fd458c875c7caae6a6a3111bea15800114d275bf3105551784a4d438ad57f8b2a5e4cf2ffb13420e5fa806df5c6b4ed8aab82fceabd5dc38e887ff327d2c0afa2d7847c2478a4c80b422ea6da5aef564046da772f24a943c7f171cdd56188b9bc7b105762a45a1fc5478a02a1d338bed5b084e7c72195a37c41aeb4b171437a464d94b5f099b3987aa91e5af685fe9605ea51d362b05596ca55243ff5884c75742f2a21d0b25234cc1dd08192569167d14a27af4634b51122722250d05d0010c00ca04c053959a3bf8327a3c21398ff4a54ab002ee83e4e4b010f12152c32136c1a093a16da2dba1fe4d45b3a634cf34a72a976635516bce37904cff9621c93a2e0641e5ef1c6d76c6c48c323732c32dfde0dcbc6abed4261d0d3e1072dc5468487711df62cc79bfcc08579c9e25d7fb0ce176d2ef8ad69f38c2a180cc5b5963c89be7c64732caf5e328a5705641033c7b3921d03da10f99e97b5b8ae7bb6f6a9f664fe67ec37207aba8167f170cdb8d4fe532160cf8e86ad21379ff701340bfe1025c996c67067572a1965e18811dfc305757441201f5f2324cff51c0da67cf767301fb3290a7f7fdaad1e0573ae5373bbb3ecaa5e11f825f984f46ffb2bcf315bb786aa44697ef4b48257402ac9a6422ecb461838dabaa2064d4bca296b98a75126eea5971120aa392c4e32bd9a8d3e4b8ca8989b11d0d1',
            'isAsync': 'true',
        }
        res = await sess.post(self.LOGIN_URL, data=data)
        res = await res.json(content_type=None)
        if res['status'] != 2000:
            return res['message']
        token = res['result']['token']
        params = {
            'token': token,
            'callbackURL': 'https://music.migu.cn/v3',
            'relayState': '',
            'logintype': 'PWD',
        }
        async with sess.get(self.LOGIN_CALLBACK_URL, params=params) as res:
            assert res.status == 200
        return 0

    def check_login(self) -> tuple:
        return {
            'PWD': self.__login_by_password,
        }
