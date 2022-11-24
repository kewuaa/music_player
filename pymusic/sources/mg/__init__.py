from urllib.parse import quote
from random import choice
from hashlib import sha1
from re import compile
from base64 import b64decode
from io import BytesIO
import asyncio
import json

from lxml.html import fromstring
from PIL import Image

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
    PUBLICKEY_URL = 'https://passport.migu.cn/password/publickey'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str | None = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self._headers['Referer'] = 'https://music.migu.cn/v3'
        self.__parser = aiofile.AWrapper(fromstring)
        self.__app_info = self._loop.create_task(self.__init_migu_app())
        self.__publickey = self._loop.create_task(self.__init_publickey())
        self.__data = self._loop.create_task(self.__load_data())

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

    async def __init_publickey(self) -> RSA:
        """初始化公钥."""

        sess = await self._session()
        resp = await sess.post(self.PUBLICKEY_URL)
        resp = await resp.json(content_type=None)
        if resp['status'] != 2000:
            raise RuntimeError('get publickey error: ' + resp['message'])
        publickey = resp['result']
        n, e = publickey['modulus'], publickey['publicExponent']
        rsa = RSA(n, e)
        return rsa

    async def __load_data(self):
        async with aiofile.async_open(self._cp / 'data.txt', 'r') as f:
            data = await f.read()
        return dict(
            line.split('=', 1)
            for line in data.strip().split('\n')
        )

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
            'type': 2,  # """ type: 标准:1 高品:2 无损:3,至臻:4 3D:5 """
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
        *_,
    ) -> None:
        sess = await self._session()
        app_info = await self.__app_info
        publickey = await self.__publickey
        login_data = await self.__data
        data = {
            'sourceID': app_info['SOURCE_ID'],
            'appType': '0',
            'relayState': '',
            'loginID': publickey.encrypt(login_id),
            'enpassword': publickey.encrypt(password),
            'captcha': '',
            'imgcodeType': '1',
            'rememberMeBox': '1',
            'fingerPrint': login_data['fingerPrint'],
            'fingerPrintDetail': login_data['fingerPrintDetail'],
            'isAsync': 'true',
        }
        resp = await sess.post(self.LOGIN_URL, data=data)
        resp = await resp.json(content_type=None)
        if resp['status'] != 2000:
            raise RuntimeError(resp['message'])
        token = resp['result']['token']
        login_callback_url = resp['result']['redirectURL']
        params = {
            'callbackURL': 'https://music.migu.cn/v3',
            'relayState': '',
            'token': token,
            'logintype': 'PWD',
        }
        async with sess.get(login_callback_url, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError('unknown error occured')
        await self.save_config(password=password, login_id=login_id)

    async def __login_by_qr(self, callback, *_) -> Image:
        check_login = None
        try:
            qrimg = await self.__fetch_qrimg()
            return qrimg
        finally:
            if check_login is not None:
                task = self._loop.create_task(check_login())
                task.add_done_callback(callback)

    async def __fetch_qrimg(self) -> Image:
        sess = await self._session()
        qr_url = 'https://passport.migu.cn/api/qrcWeb/qrcLogin'
        app_info = await self.__app_info
        params = {
            'sourceID': app_info['SOURCE_ID'],
        }
        data = {
            'isAsync': 'true',
            'sourceid': app_info['SOURCE_ID'],
        }
        resp = await sess.post(qr_url, data=data, params=params)
        resp_dict = await resp.json(content_type=None)
        if resp_dict['status'] != 2000:
            raise RuntimeError('get qrcurl error')
        b64_str: str = resp_dict['result']['qrcUrl']
        prefix = 'data:image/jpeg;base64,'
        if b64_str.startswith(prefix):
            b64_str = b64_str[len(prefix):]
        qrimg_data = b64decode(b64_str)
        qrimg = BytesIO(qrimg_data)
        qrimg = Image.open(qrimg)
        return qrimg

    async def __check_qr_login_status(self) -> None:
        await asyncio.sleep(3)

    def __login_by_sms(self) -> tuple:
        async def send_sms(cellphone: str) -> None:
            sess = await self._session()
            app_info = await self.__app_info
            login_data = await self.__data
            sms_url = 'https://passport.migu.cn/login/dynamicpassword'
            params = {
                'isAsync': 'true',
                'msisdn': login_data['msisdn'],
                'captcha': '',
                'sourceID': app_info['SOURCE_ID'],
                'imgcodeType': 2,
                'fingerPrint': login_data['fingerPrint'],
                'fingerPrintDetail': login_data['fingerPrintDetail'],
                '_': self._get_time_stamp(bit=13),
            }
            resp = await sess.get(sms_url, params=params)
            resp_dict = await resp.json(content_type=None)
            __import__('pprint').pprint(resp_dict)
            if resp_dict['status'] != 2000:
                raise RuntimeError(resp_dict['message'])
            nonlocal last_cellphone
            last_cellphone = cellphone

        async def login(cellphone: str, verify_code: str):
            if not last_cellphone:
                raise RuntimeError('it seems that you have not sended sms yet')
            elif cellphone != last_cellphone:
                raise RuntimeError('the cellphone is not the same as the last')
            sess = await self._session()
            app_info = await self.__app_info
            publickey = await self.__publickey
            login_data = await self.__data
            login_url = 'https://passport.migu.cn/authn/dynamicpassword'
            data = {
                'sourceID': app_info['SOURCE_ID'],
                'appType': 0,
                'relayState': '',
                'msisdn': login_data['msisdn'],
                'securityCode': 4053,
                'captcha': '',
                'imgcodeType': 2,
                'dynamicPassword': publickey.encrypt(verify_code),
                'fingerPrint': login_data['fingerPrint'],
                'fingerPrintDetail': login_data['fingerPrintDetail'],
                'isAsync': 'true',
            }
            resp = await sess.post(login_url, data=data)
            resp_dict = await resp.json(content_type=None)
            if resp_dict['status'] != 2000:
                raise RuntimeError(resp_dict['message'])
            token = resp_dict['result']['token']
            login_callback_url = resp_dict['result']['redirectURL']
            params = {
                'callbackURL': 'https://music.migu.cn/v3',
                'relayState': '',
                'token': token,
                'logintype': 'PWD',
            }
            async with sess.get(login_callback_url, params=params) as resp:
                if resp.status != 200:
                    raise RuntimeError('unknown error occured')

        last_cellphone = ''
        return send_sms, login

    def check_login(self) -> LoginConfig:
        return LoginConfig(
            check_id=False,
            PWD_callback=(self.__login_by_pwd,),
            # QR_callback=(self.__login_by_qr,),
            SMS_callback=self.__login_by_sms(),
        )
