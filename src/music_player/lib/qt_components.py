import asyncio
from typing import Optional

from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QMessageBox, QWidget
from music_api import Template

from .media_player import Player


class SongLable(QLabel):
    """ label to display song information and support double clicked."""

    def __init__(
        self,
        song_info: Template.SongInfo,
        parent: Optional[QWidget] = None
    ) -> None:
        """ initialize.

        :parent parent: parent widget
        """

        super().__init__(song_info.desc, parent)
        self._info = song_info
        self._player = Player()

    async def _fetch_song(self) -> Template.Song:
        """ fetch song."""

        api = self._info.master
        song = await api.fetch_song(self._info)
        return song

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        def callback(fut: asyncio.Task[Template.Song]) -> None:
            exception = fut.exception()
            if exception is not None:
                raise exception
            song = fut.result()
            assert type(song) is Template.Song
            if song.status == song.Status.NeedLogin:
                QMessageBox.information(self, "info", "need log in")
            elif song.status == song.Status.NeedVIP:
                QMessageBox.information(self, "info", "need vip")
            elif song.status == song.Status.Success:
                self._player.play_song(song)
        self._player.set_mode(None)
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._fetch_song())
        task.add_done_callback(callback)
        return super().mouseDoubleClickEvent(event)
