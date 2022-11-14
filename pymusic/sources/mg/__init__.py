from urllib.parse import quote
from random import choice
from hashlib import sha1
import asyncio
import json

from lxml.html import fromstring
from re import compile

from pymusic.lib import aiofile
from pymusic.lib.RSA import RSA
from pymusic.lib.AES import encrypt
from ..model import SongInfo
from ..model import SourceModel
from ..model import LoginConfig


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
        browser: str | None = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self.__parser = aiofile.AWrapper(fromstring)
        self.__app_info = self._loop.create_task(self.__init_migu_app())
        self.__publickey = self._loop.create_task(self.__init_publickey())

    async def _init_cookies(self) -> None:
        self.__init_migu_cookie_id()

    async def __init_migu_app(self):
        """初始化咪咕参数."""

        sess = await self._session()
        url = 'https://music.migu.cn/v3'
        resp = await sess.get(url)
        source_page = await resp.text()
        app_info = compile(r'var MUSIC_CONFIG.*?{([\S\s]+?)}').\
            search(source_page).group(1)
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

        sess = await self._session()
        resp = await sess.post(self.PUBLICKEY_URL)
        resp = await resp.json(content_type=None)
        if resp['status'] != 2000:
            raise RuntimeError('get publickey error: ' + resp['message'])
        return resp['result']

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
                summary=summary,
                _id=source_id,
                _from=self,
            )

        return [parse(tree) for tree in data]

    async def _get_info(self, name: str) -> SongInfo:
        sess = await self._session()
        sess.headers['Referer'] = 'https://music.migu.cn/v3'
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
        resp = await sess.get(self.SEARCH_URL, params=params)
        res_text = await resp.text()
        tree = await self.__parser(res_text)
        data = tree.xpath('//div[@class="songlist-body"]/div')
        return self.__parse_data(data)

    async def _get_source(self, source_id: str) -> str:
        sess = await self._session()
        sess.headers['Referer'] = 'https://music.migu.cn/v3/music/player/audio'
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
        resp = await sess.get(
            self.SOURCE_URL,
            params=params,
            allow_redirects=False,
        )
        resp = await resp.json(content_type=None)
        # N000000 未登录
        # N000001 参数不合法
        status_code = resp['returnCode']
        if status_code != '000000':
            if status_code == 'N000000':
                return -1
            else:
                raise RuntimeError('get source error:' + resp['msg'])
        url = resp['data']['playUrl']
        if url:
            return 'https:' + url

    async def __login_by_pwd(
        self,
        login_id: str,
        password: str,
        *args,
    ) -> int:
        sess = await self._session()
        app_info = await self.__app_info
        publickey = await self.__publickey
        n, e = publickey['modulus'], publickey['publicExponent']
        rsa = RSA(n, e)
        if not hasattr(self, '_fingerPrintDetail'):
            async with aiofile.async_open(self._cp / 'data.txt', 'r') as f:
                self._fingerPrintDetail = (await f.read()).strip()
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
            'fingerPrintDetail': self._fingerPrintDetail,
            'isAsync': 'true',
        }
        resp = await sess.post(self.LOGIN_URL, data=data)
        resp = await resp.json(content_type=None)
        if resp['status'] != 2000:
            return resp['message']
        token = resp['result']['token']
        params = {
            'callbackURL': 'https://music.migu.cn/v3',
            'relayState': '',
            'token': token,
            'logintype': 'PWD',
        }
        sess.headers['Referer'] = 'https://passport.migu.cn/'
        for cookie in sess.cookie_jar:
            print(cookie)
        async with sess.get(self.LOGIN_CALLBACK_URL, params=params) as resp:
            print(await resp.text())
            assert resp.status == 200
        return 0

    def check_login(self) -> LoginConfig:
        return LoginConfig(
            check_id=False,
            PWD_callback=self.__login_by_pwd,
        )
