import asyncio

from ..model import SongInfo
from ..model import SourceModel


class Source(SourceModel):
    """QQ."""

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ):
        super().__init__(loop, browser=browser)
