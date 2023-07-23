from enum import IntEnum
from threading import Lock
from typing import Optional

from music_api import Template
from PySide6.QtCore import QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QWidget


class PlayMode(IntEnum):
    """ music play mode."""

    RandomPlay = 0
    LoopPlay = 1
    SinglePlay = 2


class Player:
    """ media player."""

    __lock = Lock()
    __instance: Optional["Player"] = None
    __initialzed = False

    def __new__(cls, *args, **kwargs) -> "Player":
        """ make single instance."""

        _ = args
        _ = kwargs
        if cls.__instance is None:
            with cls.__lock:
                cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """ initialize.

        :param parent: parent widget
        """

        if self.__initialzed:
            return
        with self.__lock:
            self._audio_output = QAudioOutput()
            self._player = QMediaPlayer(parent)
            self._player.setAudioOutput(self._audio_output)
            self._play_mode: Optional[PlayMode] = None
            self._play_list: list[Template.Song] = []
            self._play_index = 0
            self._current_song: Optional[Template.Song] = None

            self.playingChanged = self._player.playingChanged
            self.durationChanged = self._player.durationChanged
            self.positionChanged = self._player.positionChanged
            self.mutedChanged = self._audio_output.mutedChanged
            self.listChanged = Signal()

            self.__initialzed = True

    def is_playing(self) -> bool:
        """ if media player is playing."""

        return self._player.isPlaying()

    def previous(self) -> None:
        """ previous song."""

        if self._play_mode is None:
            return

    def next(self) -> None:
        """ next song."""

        if self._play_mode is None:
            return

    def play(self) -> None:
        """ start to playing."""

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

        return self._current_song is not None

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

    def play_song(self, song: Template.Song) -> None:
        """ play a media source.

        :param url: media source url
        :param mode: play mode
        """

        url = song.url
        if url.startswith("http"):
            source = QUrl(url)
        else:
            source = QUrl.fromLocalFile(url)
        self._current_song = song
        self._player.setSource(source)
        self._player.play()

    def play_song_at(self, index: int) -> None:
        """ play song at list.

        :param index: index of song
        """

        song = self._play_list[index]
        self._play_index = index
        self.play_song(song)

    def extend_play_list(self, *songs: Template.Song) -> None:
        """ extend songs to play list.

        :param songs: songs to extend
        """

        self._play_list.extend(songs)
        self.listChanged.emit()
