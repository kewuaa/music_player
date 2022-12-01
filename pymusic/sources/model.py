from typing import Callable
from typing import Sequence
from typing import Tuple
from typing import Dict
from typing import List
from http.cookies import SimpleCookie
from dataclasses import dataclass
from pathlib import Path
import asyncio
import time

from aiohttp import ClientSession
from aiohttp import request

from pymusic.lib import aiofile
from pymusic.lib.logger import logger
from pymusic import settings
from .headers import UA


__stdout = None


def set_stdout(stdout: Callable[[str], None]) -> None:
    global __stdout
    __stdout = stdout


@dataclass(repr=False, order=False, eq=False)
class LoginConfig:
    message: str = 'The login function is not completed yet'
    check_id: bool = True
    PWD_callback: Tuple[Callable] | None = None
    QR_callback: Tuple[Callable] | None = None
    SMS_callback: Tuple[Callable] | None = None

    def __post_init__(self) -> None:
        self.enabled = True \
            if any([self.PWD_callback, self.QR_callback, self.SMS_callback])\
            else False


class SourceModel:
    """Source类的模板."""

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        path: str,
        browser: str | None = None,
    ) -> None:
        self._loop = loop
        self._headers: Dict = UA.get(browser or 'chrome')
        self._cookies = {}
        self._cp = Path(path).parent
        self.__config_path = settings.config_path / self._cp.name / '.config'
        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        if self.__config_path.exists():
            self.__config_exist = True
            logger.info(f'detect config file in {self.__config_path}')
        else:
            self.__config_exist = False
            logger.info(f'do not find config file in {self.__config_path}')
        self.__sess = asyncio.futures.Future(loop=loop)

        def init_sess() -> None:
            future: asyncio.tasks.Task = loop.create_task(self.__init_sess())
            asyncio.futures._chain_future(future, self.__sess)

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

    async def _session(self) -> ClientSession:
        return await self.__sess

    async def _init_cookies(self) -> None:
        """初始化cookie."""

        pass

    async def _get_info(self, name: str) -> List:
        """检索获取信息.

        :param name: 检索项
        :returns: source information
        """
        raise NotImplementedError

    async def _get_source(self, source_id: str) -> str:
        """获取source.

        :param source_id: source的id
        :returns: source
        """
        raise NotImplementedError

    async def check_settings(self) -> Dict:
        """检查是否存在配置文件."""

        config_path = self.__config_path
        config = {}
        if self.__config_exist:
            async with aiofile.async_open(config_path, 'r') as f:
                for line in await f.readlines():
                    k, v = line.split('=', 1)
                    config[k] = v.strip()
        return config

    async def save_config(self, **kwargs) -> None:
        config_path = self.__config_path
        config = await self.check_settings()
        if kwargs:
            config.update(kwargs)
            async with aiofile.async_open(
                config_path,
                'w',
                encoding='utf-8',
            ) as f:
                for k, v in config.items():
                    await f.write(f'{k}={v}\n')
            logger.info(f'{kwargs} has been saved to: {config_path}')

    def check_login(self) -> LoginConfig:
        """登录.

        返回允许的登录方式.
        """

        config = LoginConfig()
        logger.info(config.message)
        return config

    def _cookie_str2dict(self, cookies: str) -> Dict:
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

        sess: ClientSession = await self.__sess
        if not sess.closed:
            await sess.close()
        logger.info('session closed')


class SongInfo:
    def __init__(
        self,
        *,
        summary: Sequence[str],
        _id: Sequence | str,
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

    async def url(self) -> str:
        url = getattr(self, '_url', None)
        if url is None:
            url = await self.__from._get_source(self.__id)
        if type(url) is str:
            self._url = url
            return url
        if url is None:
            msg = 'vip或无版权歌曲'
        elif url == -1:
            msg = '你还没有登录\n请先登录'
        stdout = globals().get('__stdout') or logger.info
        stdout(msg)

    async def download(self) -> None:
        if not hasattr(self, '_path'):
            url: str = await self.url()
            if url is None:
                logger.warning('could not get url successfully')
                raise RuntimeError('could not get url successfully')
            suffix: str = url.split('.')[-1]
            name = self.__name + '.' + suffix
            self._path = path = self.__base_path / name
            async with request('GET', url) as res:
                data = await res.read()
                async with aiofile.async_open(path, 'wb') as f:
                    await f.write(data)
        logger.info(f'{self.__name} already in {self._path}')

    def check_download(self) -> Path | None:
        if not hasattr(self, '_path'):
            files = list(self.__base_path.glob(self.__name + '.*'))
            if not files:
                return
            self._path = files[0]
        return self._path
