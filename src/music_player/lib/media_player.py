import asyncio
from enum import IntEnum
from threading import Lock
from typing import Iterator, Optional

from music_api import Template
from PySide6.QtCore import QObject, QUrl, Signal, SignalInstance
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QMessageBox, QWidget


class PlayMode(IntEnum):
    """ music play mode."""

    SinglePlay = 0
    LoopPlay = 1
    RandomPlay = 2


class Player(QObject):
    """ media player."""

    __lock = Lock()
    __instance: Optional["Player"] = None
    __initialzed = False
    listAdd: SignalInstance = Signal(tuple) # pyright: ignore
    listRemove: SignalInstance = Signal(tuple) # pyright: ignore

    def __new__(cls, *args, **kwargs) -> "Player":
        """ make single instance."""

        _ = args
        _ = kwargs
        if cls.__instance is None:
            with cls.__lock:
                cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        loop: Optional[asyncio.base_events.BaseEventLoop] = None
    ) -> None:
        """ initialize.

        :param parent: parent widget
        """

        if self.__initialzed:
            return
        with self.__lock:
            self._parent = parent
            self._loop = loop if loop is not None else asyncio.get_event_loop()
            self._audio_output = QAudioOutput()
            self._player = QMediaPlayer(parent)
            self._player.setAudioOutput(self._audio_output)
            self._play_mode: Optional[PlayMode] = None
            self._play_list: list[Template.Song] = []
            self._play_index = 0
            self._current_media: Optional[Template.Song] = None

            self.playingChanged = self._player.playingChanged
            self.mediaStatusChanged = self._player.mediaStatusChanged
            self.durationChanged = self._player.durationChanged
            self.positionChanged = self._player.positionChanged
            self.mutedChanged = self._audio_output.mutedChanged

            super().__init__(parent)

            self.__initialzed = True

    def is_playing(self) -> bool:
        """ if media player is playing."""

        return self._player.isPlaying()

    def previous(self) -> None:
        """ previous media."""

        if self._play_mode is None or self._play_mode is PlayMode.SinglePlay:
            return
        elif self._play_mode is PlayMode.LoopPlay:
            self._play_index -= 1
            if self._play_index > 0:
                self.play_media_at(self._play_index)
            else:
                self._play_index = len(self._play_list)
                self.play_media_at(self._play_index)

    def next(self) -> None:
        """ next media."""

        if self._play_mode is None or self._play_mode is PlayMode.SinglePlay:
            return
        elif self._play_mode is PlayMode.LoopPlay:
            self._play_index += 1
            if self._play_index < len(self._play_list):
                self.play_media_at(self._play_index)
            else:
                self._play_index = 0
                self.play_media_at(0)

    def play(self) -> None:
        """ start to play."""

        self._player.play()

    def pause(self) -> None:
        """ stop playing."""

        self._player.pause()

    def stop(self) -> None:
        self._player.stop()

    def set_position(self, pos: int) -> None:
        """ set the position for media player."""

        self._player.setPosition(pos)

    def has_source(self) -> bool:
        """ if the player has source."""

        return self._current_media is not None

    def is_muted(self) -> bool:
        """ if the media player is muted."""

        return self._audio_output.isMuted()

    def set_muted(self, muted: bool) -> None:
        """ mute media player."""

        self._audio_output.setMuted(muted)

    def set_volume(self, volume: int) -> None:
        """ set volume."""

        self._audio_output.setVolume(volume / 100)

    def set_mode(self, mode: Optional[PlayMode]) -> None:
        """ set play mode.

        :param mode: play mode
        """

        self._play_mode = mode

    def set_playback_rate(self, rate: float) -> None:
        """ set playback rate.

        :param rate: rate to set
        """

        self._player.setPlaybackRate(rate)

    def play_media(self, song: Template.Song) -> None:
        """ play a media source.

        :param url: media source url
        :param mode: play mode
        """

        def play(url: str) -> None:
            if url.startswith("http"):
                source = QUrl(url)
            else:
                source = QUrl.fromLocalFile(url)
            self._current_media = song
            if self._player.isPlaying():
                self._player.stop()
                self._loop.call_soon(
                    lambda: (self._player.setSource(source), self._player.play())
                )
            else:
                self._player.setSource(source)
                self._player.play()

        def callback(fut: asyncio.Task[tuple[Template.Song.Status, str]]) -> None:
            exception = fut.exception()
            if exception is not None:
                raise exception
            status, url = fut.result()
            if status is Template.Song.Status.NeedLogin:
                QMessageBox.information(self._parent, "info", "need log in")
                self.next()
            elif status is Template.Song.Status.NeedVIP:
                QMessageBox.information(self._parent, "info", "need vip")
                self.next()
            elif status is Template.Song.Status.Success:
                play(url)

        if song.url:
            play(song.url)
        else:
            self._loop.create_task(song.fetch()).add_done_callback(callback)

    def schedule(self) -> None:
        """ schedule when end of media."""

        if self._play_mode is None:
            self._player.stop()
        elif self._play_mode is PlayMode.SinglePlay:
            self._player.setPosition(0)
            self._player.play()
        else:
            self.next()

    def play_media_at(self, index: int) -> None:
        """ play a media at list.

        :param index: index of media
        """

        song = self._play_list[index]
        self._play_index = index
        self.play_media(song)

    def __getitem__(self, index: int) -> Template.Song:
        return self._play_list[index]

    def __len__(self) -> int:
        return len(self._play_list)

    def __iter__(self) -> Iterator[Template.Song]:
        return iter(self._play_list)

    def extend_play_list(self, *songs: Template.Song) -> None:
        """ extend songs to play list.

        :param songs: songs to extend
        """

        to_emit = []
        for song in songs:
            if song not in self._play_list:
                self._play_list.append(song)
                to_emit.append(song)
        self.listAdd.emit(to_emit)

    def remove_from_list(self, *index: int) -> None:
        """ remove a media source at list.

        :param index: index of the medai
        """

        for i in sorted(index, reverse=True):
            self._play_list.pop(i)
        self.listRemove.emit(index)
