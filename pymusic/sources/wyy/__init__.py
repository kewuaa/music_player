import json
import base64
import asyncio

from Crypto.Cipher import AES
from hashlib import md5

from ..model import SongInfo
from ..model import SourceModel
from ..model import LoginConfig


class Source(SourceModel):
    """网易云."""

    SEARCH_URL = 'https://music.163.com/weapi/cloudsearch/get/web'
    SOURCE_URL = 'https://music.163.com/weapi/song/enhance/player/url/v1'
    LOGIN_URL_PHONE = 'https://music.163.com/weapi/login/cellphone'
    LOGIN_URL_EMAIL = 'http://music.163.com/weapi/login'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)

    def __AES(self, to_encrypt: str, key: str) -> str:
        """AES加密."""

        to_encrypt = to_encrypt.encode()
        pad = 16 - len(to_encrypt) % 16
        to_encrypt += chr(pad).encode() * pad
        aes = AES.new(key.encode(), AES.MODE_CBC, '0102030405060708'.encode())
        result = aes.encrypt(to_encrypt)
        return base64.b64encode(result).decode()

    encSecKey = '21e8dcd7b013c2e56af244ad4e55484d5840b108df255fbeccf88e818736'\
        '2476af2cc881a61884aea955937337fe3bdfe896a62c27606da8aea2f3c93b9bb6c6'\
        'e0c17b85da6e3a766d580286967975db7f0f38ef88d582b39f92058deff794b70570'\
        '2e70be6f26b93c206e55e55e6a51874469fd11cdff86df742c3b9dd89abe'
    i = 'jkUEeutwbd2HLFNL'
    g = '0CoJUm6Qyw8W8jud'

    def __encrypt(self, to_encrypt: str) -> str:
        encrypt_str = self.__AES(to_encrypt, self.g)
        encrypt_str = self.__AES(encrypt_str, self.i)
        return encrypt_str

    def __parse_data(self, data: dict) -> list:
        """解析data."""

        def parse(data: dict) -> SongInfo:
            song_name = data['name']
            singer_name = data['ar'][0]['name']
            album_name = data['al']['name']
            source_id = data['id']
            summary = [song_name, singer_name, album_name]
            return SongInfo(
                summary=summary,
                _id=source_id,
                _from=self,
            )

        return [parse(item) for item in data]

    async def _get_info(self, name: str) -> SongInfo:
        params = {
            'csrf_token': '',
        }
        to_encrypt = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "s": name,
            "type": '1',
            "offset": '0',
            "total": "true",
            "limit": "30",
            "csrf_token": "",
        }
        to_encrypt = json.dumps(to_encrypt)
        encrypt_str = self.__encrypt(to_encrypt)
        data = {
            'params': encrypt_str,
            'encSecKey': self.encSecKey,
        }
        sess = await self._session()
        resp = await sess.post(self.SEARCH_URL, params=params, data=data)
        resp_dict = await resp.json(content_type=None)
        data = resp_dict.get('result')
        if data is None:
            raise RuntimeError('unknow error while getting source info')
        data = data['songs']
        return self.__parse_data(data)

    async def _get_source(self, source_id) -> str:
        params = {
            'csrf_token': '',
        }
        to_encrypt = {
            'ids': f'[{source_id}]',
            'level': 'standard',
            'encodeType': 'aac',
            'csrf_token': '',
        }
        to_encrypt = json.dumps(to_encrypt)
        encrypt_str = self.__encrypt(to_encrypt)
        data = {
            'params': encrypt_str,
            'encSecKey': self.encSecKey,
        }
        sess = await self._session()
        resp = await sess.post(self.SOURCE_URL, params=params, data=data)
        resp = await resp.json(content_type=None)
        url = resp['data'][0]['url']
        if url is not None:
            return url

    async def __login_by_pwd(
        self,
        login_id,
        password,
        *args,
    ) -> int:
        """账号密码登录."""

        password = md5(password.encode()).hexdigest()
        if '@' in login_id:
            data = {
                'username': login_id,
                'password': password,
                'rememberLogin': 'true',
                'clientToken': '1_jVUMqWEPke0/1/Vu56xCmJpo5vP1grjn_SOVVDzOc78w'
                '8OKLVZ2JH7IfkjSXqgfmh',
            }
            url = self.LOGIN_URL_EMAIL
        else:
            data = {
                'phone': login_id,
                'password': password,
                'rememberLogin': 'true',
            }
            url = self.LOGIN_URL_PHONE
        params = {
            'csrf_token': '',
        }
        to_encrypt = json.dumps(data)
        encrypt_str = self.__encrypt(to_encrypt)
        data = {
            'params': encrypt_str,
            'encSecKey': self.encSecKey,
        }
        sess = await self._session()
        resp = await sess.post(url, params=params, data=data)
        resp_dict = await resp.json(content_type=None)
        resp_code = resp_dict['code']
        print(resp_dict)
        print(sess.headers)
        for cookie in sess.cookie_jar:
            print(cookie)
        if resp_code != 200:
            raise RuntimeError(resp_dict.get('msg', '登录失败'))
        return 1

    def check_login(self) -> LoginConfig:
        return LoginConfig(
            check_id=False,
            PWD_callback=self.__login_by_pwd,
        )
