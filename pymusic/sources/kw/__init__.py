from time import time
from ctypes import c_uint32
from secrets import randbelow
from http.cookies import SimpleCookie
import asyncio

from aiohttp import ClientSession

from ..model import SongInfo
from ..model import SourceModel


def int_overflow(val: int) -> int:
    maxint = 2 ** 31
    if not -maxint <= val <= maxint - 1:
        val = (val + maxint) % (2 * maxint) - maxint
    return val


def unsigned_right_shitf(n, i):
    # 数字小于0，则转为32位无符号uint
    if n < 0:
        n = c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


def reqid():
    r = None
    o = None
    d = 0

    def get_reqid():
        nonlocal r, o, d
        b = []
        f = r
        v = o
        if f is None or v is None:
            m = [randbelow(256) for _ in range(16)]
            r = f = f or [1 | m[0], m[1], m[2], m[3], m[4], m[5]]
            o = v = v or 16383 & (int_overflow(m[6] << 8) | 7)
        y = int(time() * 1000)
        w = d + 1
        d = w
        x = (10000 * (268435455 & (y := y + 12219292800000)) + w) % 4294967296
        b.append(unsigned_right_shitf(x, 24) & 255)
        b.append(unsigned_right_shitf(x, 16) & 255)
        b.append(unsigned_right_shitf(x, 8) & 255)
        b.append(255 & x)
        _x = int(y / 4294967296 * 10000) & 268435455
        b.append(unsigned_right_shitf(_x, 8) & 255)
        b.append(255 & _x)
        b.append(unsigned_right_shitf(_x, 24) & 15 | 16)
        b.append(unsigned_right_shitf(_x, 16) & 255)
        b.append(unsigned_right_shitf(v, 8) | 128)
        b.append(255 & v)
        b.extend(f)
        result = [f'{hex(i)[2:]:0>2}' for i in b]
        result.insert(10, '-')
        result.insert(8, '-')
        result.insert(6, '-')
        result.insert(4, '-')
        return ''.join(result)
    return get_reqid


class Source(SourceModel):
    """酷我."""

    SEARCH_URL = 'https://www.kuwo.cn/api/www/search/searchMusicBykeyWord'
    SOURCE_URL = 'https://www.kuwo.cn/api/v1/www/music/playUrl'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self.__domain = 'https://www.kuwo.cn/'
        self._headers['Referer'] = self.__domain
        self.__get_reqid = reqid()

    def __parse_data(self, data: list) -> list:
        def parse(item: dict) -> SongInfo:
            name = item['name']
            author = item['artist']
            album = item['album']
            summary = [name, author, album]
            source_id = item['rid']
            return SongInfo(
                summary=summary,
                _id=source_id,
                _from=self,
            )

        return [parse(item) for item in data]

    async def _init_cookies(self) -> None:
        self._cookies['kw_token'] = 'LPZZ7D4HRJO'

    async def _get_info(self, name: str) -> list:
        sess: ClientSession = await self._sess
        cookies: SimpleCookie = sess.cookie_jar.filter_cookies(self.__domain)
        csrf = cookies.get('kw_token').value
        sess.headers['csrf'] = csrf
        params = {
            'key': name,
            'rn': 30,
            'httpsStatus': 1,
            'req-id': self.__get_reqid(),
        }
        res = await sess.get(self.SEARCH_URL, params=params)
        res_dict = await res.json(content_type=None)
        data = res_dict['data']['list']
        return self.__parse_data(data)

    async def _get_source(self, source_id) -> str:
        sess: ClientSession = await self._sess
        params = {
            'mid': source_id,
            'httpsStatus': 1,
            'type': 'music',
            'req-id': self.__get_reqid(),
        }
        res = await sess.get(self.SOURCE_URL, params=params)
        res_dict = await res.json(content_type=None)
        data = res_dict['data']
        return data['url']
