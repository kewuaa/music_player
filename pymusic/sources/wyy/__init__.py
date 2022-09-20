import asyncio

from Crypto.Cipher import AES

from ..model import SongInfo
from ..model import SourceModel


class Source(SourceModel):
    """网易云."""

    SEARCH_URL = 'https://music.163.com/weapi/cloudsearch/get/web'

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)

    def _get_info(self, name: str) -> SongInfo:
        params = {
            'csrf_token': '',
        }
