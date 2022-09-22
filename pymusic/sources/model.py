from http.cookies import SimpleCookie
from pathlib import Path
import asyncio
import time

from aiohttp import ClientSession
from aiohttp import request

from pymusic.lib import aiofile
from pymusic import settings
from .headers import UA


__ua = UA()
__stdout = None


def set_stdout(stdout) -> None:
    global __stdout
    __stdout = stdout


class SourceModel:
    """Source类的模板."""

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        path: str,
        browser: str = None,
        need_verify: bool = False,
    ) -> None:
        self._loop = loop
        self._headers: dict = eval(f'__ua.{browser or "chrome"}')
        self._cookies: dict = {}
        self._cp = Path(path).parent
        self.__config_path = settings.config_path / self._cp.name
        self.__config_path.mkdir(parents=True, exist_ok=True)
        self._sess = asyncio.futures.Future(loop=loop)
        self.need_verify = need_verify

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
        await self._init_cookies()
        if self._cookies:
            kwargs['cookies'] = self._cookies
        return ClientSession(**kwargs)

    async def _init_cookies(self) -> None:
        """初始化cookie."""

        pass

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

    def check_settings(self):
        """检查是否存在配置文件."""

        config_path = self.__config_path
        if config_path.exists():
            return config_path

    def check_login(self) -> dict:
        """登录.

        返回允许的登录方式.
        """

        raise NotImplementedError

    def _cookie_str2dict(self, cookies: str) -> None:
        """将cookie字符串转换为字典.

        :param cookies: cookie字符串
        :returns: cookie字典
        """

        return {
            cookie.key: cookie.value
            for cookie in SimpleCookie(cookies).values()
        }

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


class SongInfo:
    def __init__(
        self,
        *,
        summary: list,
        _id: list or str,
        _from: SourceModel,
    ) -> None:
        self.__summary = summary
        self.__id = _id
        self.__from = _from
        self.__name = '_'.join(summary[: 2]).replace(':', '')
        self.__base_path = settings.download_path / _from._cp.name
        self.__base_path.mkdir(parents=True, exist_ok=True)

    @property
    def summary(self) -> str:
        return ' -> '.join(self.__summary)

    async def url(self):
        if not hasattr(self, '_url'):
            self._url = await self.__from._get_source(self.__id)
        url = self._url
        if type(url) is str:
            return self._url
        if url is None:
            msg = 'vip或无版权歌曲'
        elif url == -1:
            msg = '你还没有登录\n请先登录'
        stdout = globals().get('__stdout') or print
        stdout(msg)

    async def download(self) -> int:
        if not hasattr(self, '_path'):
            url: str = await self.url()
            if url is None:
                return 1
            suffix: str = url.split('.')[-1]
            name = self.__name + '.' + suffix
            self._path = path = self.__base_path / name
            async with request('GET', url) as res:
                data = await res.read()
                async with aiofile.async_open(path, 'wb') as f:
                    await f.write(data)
        return 0

    def check_download(self):
        if not hasattr(self, '_path'):
            files = list(self.__base_path.glob(self.__name + '.*'))
            if not files:
                return
            self._path = files[0]
        return self._path
