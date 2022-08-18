from http.cookies import SimpleCookie
from collections import namedtuple
from pathlib import Path
import asyncio
import time

from aiohttp import ClientSession

from .headers import UA


SongInfo = namedtuple('SongInfo', ['summary', 'id_', 'type_', 'from_'])
ua = UA()


class SourceModel:
    """Source类的模板."""

    def __init__(
            self, loop: asyncio.base_events.BaseEventLoop,
            *, path: str, browser: str = None) -> None:
        self._loop = loop
        self._headers: dict = eval(f'ua.{browser or "chrome"}')
        self._cookies: dict = {}
        self._cp = Path(path).parent
        self._sess = asyncio.futures.Future(loop=loop)

        def init_sess() -> None:
            future: asyncio.tasks.Task = loop.create_task(self.__init_sess())
            asyncio.futures._chain_future(future, self._sess)

        loop.call_soon_threadsafe(init_sess)

    async def __init_sess(self) -> ClientSession:
        """初始化会话."""

        kwargs = {
            'headers': self._headers,
            'loop': self._loop,
        }
        if self._cookies:
            kwargs['cookies'] = self._cookies
        return ClientSession(**kwargs)

    async def _get_info(self, name: str) -> list:
        """检索获取信息.

        :param name: 检索项
        :returns: source information
        """
        raise NotImplementedError

    async def _get_source(self, source_id: str) -> None:
        """获取source.

        :param source_id: source的id
        :returns: source
        """
        raise NotImplementedError

    def _cookie_str2dict(self, cookies: str) -> None:
        """将cookie字符串转换为字典.

        :param cookies: cookie字符串
        :returns: cookie字典
        """

        return {cookie.key: cookie.value
                for cookie in SimpleCookie(cookies).values()}

    def _get_time_stamp(self, bit: int = 10) -> int:
        """获取时间戳.

        :param bit: 时间戳位数
        :returns: 时间戳
        """
        t = time.time()
        return int(t * 10 ** (bit - 10))

    async def exit(self) -> None:
        """退出."""

        sess: ClientSession = await self._sess
        if not sess.closed:
            await sess.close()
