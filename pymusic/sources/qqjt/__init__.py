import asyncio

from aiohttp import ClientSession

from ..model import SongInfo
from ..model import SourceModel


class Source(SourceModel):
    """千千静听."""

    SEARCH_URL = 'https://music.91q.com/search'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
