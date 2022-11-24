from http.cookies import SimpleCookie
from hashlib import md5
import json
import base64
import asyncio

from Crypto.Cipher import AES

from ..model import SongInfo
from ..model import SourceModel
from ..model import LoginConfig


class Source(SourceModel):
    """网易云."""

    SEARCH_URL = 'https://music.163.com/weapi/cloudsearch/get/web'
    SOURCE_URL = 'https://music.163.com/weapi/song/enhance/player/url/v1'

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

    def __encrypt(self, data: dict) -> dict:
        to_encrypt = json.dumps(data)
        encrypt_str = self.__AES(to_encrypt, self.g)
        encrypt_str = self.__AES(encrypt_str, self.i)
        return {
            'params': encrypt_str,
            'encSecKey': self.encSecKey,
        }

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
        sess = await self._session()
        params = {
            'csrf_token': '',
        }
        data = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "s": name,
            "type": '1',
            "offset": '0',
            "total": "true",
            "limit": "30",
            "csrf_token": "",
        }
        data = self.__encrypt(data)
        resp = await sess.post(self.SEARCH_URL, params=params, data=data)
        resp_dict = await resp.json(content_type=None)
        data = resp_dict.get('result')
        if data is None:
            raise RuntimeError('unknow error while getting source info')
        data = data['songs']
        return self.__parse_data(data)

    async def _get_source(self, source_id) -> str:
        sess = await self._session()
        params = {
            'csrf_token': '',
        }
        data = {
            'ids': f'[{source_id}]',
            'level': 'standard',
            'encodeType': 'aac',
            'csrf_token': '',
        }
        data = self.__encrypt(data)
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
    ) -> None:
        """账号密码登录."""

        sess = await self._session()
        password = md5(password.encode()).hexdigest()
        if '@' in login_id:
            data = {
                'username': login_id,
                'password': password,
                'rememberLogin': 'true',
                'clientToken': '1_jVUMqWEPke0/1/Vu56xCmJpo5vP1grjn_SOVVDzOc78w'
                '8OKLVZ2JH7IfkjSXqgfmh',
            }
            url = 'http://music.163.com/weapi/login'
        else:
            data = {
                'phone': login_id,
                'password': password,
                'rememberLogin': 'true',
            }
            url = 'https://music.163.com/weapi/login/cellphone'
        params = {
            'csrf_token': '',
        }
        data = self.__encrypt(data)
        resp = await sess.post(url, params=params, data=data)
        resp_dict = await resp.json(content_type=None)
        resp_code = resp_dict['code']
        if resp_code != 200:
            raise RuntimeError(resp_dict.get('message', '登录失败'))

    async def __login_by_qr(self, callback, *_) -> str:
        """二维码扫描登录."""

        def cancel():
            task.remove_done_callback(callback)
            task.cancel()
        check_login = self.__check_qr_login_status
        try:
            unikey = await self.__fetch_unikey()
            return 'http://music.163.com/login?codekey=' + unikey
        except Exception as e:
            check_login = None
            raise e
        finally:
            if check_login is not None:
                task = self._loop.create_task(check_login(unikey))
                task.add_done_callback(callback)
                current_task = asyncio.tasks.current_task(loop=self._loop)
                current_task._special_callback = cancel

    async def __fetch_unikey(self) -> str:
        """获取二维码图片所需unikey."""

        sess = await self._session()
        unikey_url = 'https://music.163.com/weapi/login/qrcode/unikey'
        data = {
            'type': 1,
            'noCheckToken': 'true',
            'csrf_token': '',
        }
        data = self.__encrypt(data)
        resp = await sess.post(
            unikey_url,
            params={'csrf_token': ''},
            data=data,
        )
        resp_dict = await resp.json(content_type=None)
        if resp_dict['code'] != 200:
            raise RuntimeError('get unikey error')
        unikey = resp_dict['unikey']
        return unikey

    async def __check_qr_login_status(self, unikey: str) -> None:
        """检测二维码是否扫描成功."""

        sess = await self._session()
        check_url = 'https://music.163.com/weapi/login/qrcode/client/login'
        account_url = 'https://music.163.com/weapi/w/nuser/account/get'
        data = {
            'csrf_token': '',
            'key': unikey,
            'type': 1,
        }
        data = self.__encrypt(data)
        while 1:
            await asyncio.sleep(0.5)
            resp = await sess.post(
                check_url,
                params={'csrf_token': ''},
                data=data,
            )
            resp_dict = await resp.json(content_type=None)
            code = resp_dict['code']
            if code == 803:
                break
            elif code in [801, 802]:
                continue
            else:
                raise RuntimeError('unknown error')
        cookies: SimpleCookie = \
            sess.cookie_jar.filter_cookies('https://music.163.com/')
        csrf_token = cookies.get('__csrf')
        csrf_token = '' if csrf_token is None else csrf_token.value
        data = self.__encrypt({'csrf_token': csrf_token})
        resp = await sess.post(
            account_url,
            params={'csrf_token': csrf_token},
            data=data,
        )
        # resp_dict = await resp.json(content_type=None)

    def __login_by_sms(self, ctcode: int = 86) -> None:
        """通过短信验证码登录."""

        async def send_sms(cellphone: str) -> None:
            """发送验证码."""

            sess = await self._session()
            sms_url = 'http://music.163.com/weapi/sms/captcha/sent'
            data = {
                'cellphone': cellphone,
                'ctcode': ctcode,
            }
            data = self.__encrypt(data)
            resp = await sess.post(
                sms_url,
                data=data,
                params={'csrf_token': ''},
            )
            resp_dict = await resp.json(content_type=None)
            if resp_dict['code'] != 200:
                raise RuntimeError('send sms error')
            nonlocal last_cellphone
            last_cellphone = cellphone

        async def login(cellphone: str, verify_code: str) -> None:
            if not last_cellphone:
                raise RuntimeError('it seems that you have not sended sms yet')
            elif cellphone != last_cellphone:
                raise RuntimeError('the cellphone is not the same as the last')
            sess = await self._session()
            verify_url = 'http://music.163.com/weapi/sms/captcha/verify'
            cookies = sess.cookie_jar.filter_cookies('https://music.163.com/')
            csrf_token = cookies.get('__csrf')
            csrf_token = '' if csrf_token is None else csrf_token.value
            data = {
                'cellphone': cellphone,
                'captcha': verify_code,
                'ctcode': ctcode,
                'csrf_token': csrf_token,
            }
            data = self.__encrypt(data)
            resp = await sess.post(
                verify_url,
                data=data,
                params={'csrf_token': csrf_token},
            )
            resp_dict = await resp.json(content_type=None)
            resp_code = resp_dict['code']
            if resp_code != 200:
                raise RuntimeError(resp_dict.get('msg', resp_dict['message']))

        last_cellphone = ''
        return send_sms, login

    def check_login(self) -> LoginConfig:
        return LoginConfig(
            check_id=False,
            PWD_callback=(self.__login_by_pwd,),
            QR_callback=(self.__login_by_qr,),
            SMS_callback=self.__login_by_sms(),
        )
