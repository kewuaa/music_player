import asyncio
from typing import Optional

from aiohttp import request
from music_api import Template
from PySide6.QtCore import QBuffer, QIODeviceBase, QSize
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from .media_player import Player


class SongLabel(QLabel):
    """ label to display song information and support double clicked."""

    def __init__(
        self,
        song: Template.Song,
        parent: Optional[QWidget] = None,
        loop: Optional[asyncio.base_events.BaseEventLoop] = None
    ) -> None:
        """ initialize.

        :parent parent: parent widget
        """

        super().__init__(song.desc, parent)
        self._song = song
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._player = Player()
        self._loop.create_task(self._set_tooltip())

    async def _set_tooltip(self) -> None:
        if self._song.img_url:
            async with request("GET", self._song.img_url) as res:
                data = await res.read()
            img = QPixmap()
            img.loadFromData(data)
            img = img.scaled(QSize(300, 300))
            buf = QBuffer()
            buf.open(QIODeviceBase.OpenModeFlag.WriteOnly)
            img.save(buf, "JPEG")
            data = buf.data().toBase64().data()
            self.setToolTip(f'<img src="data:image/jpeg;base64,{data.decode()}>')

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self._player.play_media(self._song)
        return super().mouseDoubleClickEvent(event)
