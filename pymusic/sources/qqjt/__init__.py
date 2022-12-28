from hashlib import md5
import asyncio

from ..model import SongInfo
from ..model import SourceModel
from ..model import LoginConfig


class Source(SourceModel):
    """QQ."""

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ):
        super().__init__(loop, path=__file__, browser=browser)
        self.__appid = 16073360

    def __encrypt(self, data: dict) -> str:
        secret = '0b50b02fd0d73a9c4c8c3a781c30845f'
        string = '&'.join(f'{key}={data[key]}'for key in sorted(data))
        return md5((string + secret).encode()).hexdigest()

    def __parse(self, data: list) -> list:
        def parse(item: dict) -> SongInfo:
            title = item['title']
            singer = item['artist'][0]['name']
            summary = [title, singer]
            if item.get('albumTitle') is not None:
                summary.append(item['albumTitle'])
            _id = item['TSID']
            return SongInfo(
                summary=summary,
                _id=_id,
                _from=self
            )

        return [parse(item) for item in data]

    async def _get_info(self, name: str) -> list:
        sess = await self._session()
        url = 'https://music.91q.com/v1/search'
        params = {
            'word': name,
            'type': 1,
            'appid': self.__appid,
            'pageSize': 20,
            'timestamp': self._get_time_stamp(),
        }
        params['sign'] = self.__encrypt(params),
        resp = await sess.get(url, params=params)
        resp_dict = await resp.json(content_type=None)
        if resp_dict['errno'] != 22000:
            raise RuntimeError(resp_dict['errmsg'])
        data = resp_dict['data']['typeTrack']
        return self.__parse(data)

    async def _get_source(self, source_id) -> str:
        sess = await self._session()
        url = 'https://music.91q.com/v1/song/tracklink'
        params = {
            'appid': self.__appid,
            'TSID': source_id,
            'timestamp': self._get_time_stamp(),
        }
        params['sign'] = self.__encrypt(params)
        resp = await sess.get(url, params=params)
        resp_dict = await resp.json(content_type=None)
        if resp_dict['errno'] != 22000:
            raise RuntimeError(resp_dict['errmsg'])
        return resp_dict['data']['path']

    async def __login_by_pwd(self, login_id: str, password: str) -> None:
        sess = await self._session()
        url = 'https://music.91q.com/v1/oauth/login/password'
        timestamp = self._get_time_stamp()
        data = {
            'phone': login_id,
            'password': md5(password.encode()).hexdigest(),
            'appid': self.__appid,
            'timestamp': timestamp,
        }
        params = {
            'sign': self.__encrypt(data),
            'timestamp': timestamp,
        }
        resp = await sess.post(url, params=params, data=data)
        resp_dict = await resp.json(content_type=None)
        if resp_dict['errno'] != 22000:
            raise RuntimeError(resp_dict['errmsg'])
        token = resp_dict['data']['access_token']
        sess.cookie_jar.update_cookies({
            'token_type': 'access_token',
            'access_token': token,
            'refresh_token': token,
        })

    def check_login(self) -> LoginConfig:
        return LoginConfig(
            PWD_callback=(self.__login_by_pwd,)
        )
