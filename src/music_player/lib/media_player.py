from enum import IntEnum
from threading import Lock
from typing import Optional

from PySide6.QtCore import QSize, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QLabel, QPushButton, QSlider, QWidget
from music_api import Template


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
            self._audio_output.setVolume(50)
            self._player = QMediaPlayer(parent)
            self._player.setAudioOutput(self._audio_output)
            self._play_mode: Optional[PlayMode] = None
            self._play_list: list[Template.Song] = []
            self._play_index = 0
            self._current_media: Optional[Template.Song] = None

            self._play_icon = QIcon()
            self._play_icon.addFile(
                u":pic/icons/play.png",
                QSize(),
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )
            self._pause_icon = QIcon()
            self._pause_icon.addFile(
                u":pic/icons/pause.png",
                QSize(),
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )

            self.__initialzed = True

    def connect_to_widgets(
        self,
        previous: QPushButton,
        toggle: QPushButton,
        next: QPushButton,
        stop: QPushButton,
        progress_slider: QSlider,
        progress_label: QLabel,
    ) -> None:
        """ connect to widgets.

        :param previous: previous song button
        :param toggle: toggle play state button
        :param next: next song button
        :param stop: stop song button
        :progress_slider: progress slider
        :progress_label: progress label
        """

        def previous_song() -> None:
            if self._play_mode is None:
                return

        def toggle_icon() -> None:
            if self._player.isPlaying():
                toggle.setIcon(self._play_icon)
            else:
                toggle.setIcon(self._pause_icon)

        def toggle_play_state() -> None:
            if self._current_media is None:
                return
            if self._player.isPlaying():
                self._player.pause()
            else:
                self._player.play()

        def next_song() -> None:
            if self._play_mode is None:
                return

        def stop_play() -> None:
            self._player.stop()
            progress_slider.setEnabled(False)
            progress_label.setText("00 / 00")

        def format_song_length(length: int) -> str:
            seconds = length / 1000
            minitus = int(seconds // 60)
            return f"{minitus:0>2}:{int(seconds - minitus * 60):0>2}"

        def set_progress_length(length: int) -> None:
            nonlocal song_length
            if length > 0:
                song_length = format_song_length(length)
                progress_slider.setEnabled(True)
                progress_slider.setRange(0, length)
                progress_label.setText(f"00 / {song_length}")
            else:
                progress_label.setText("00 / 00")

        def set_slider_position(pos: int) -> None:
            progress_slider.setSliderPosition(pos)
            progress_label.setText(f"{format_song_length(pos)} / {song_length}")

        song_length = 0
        previous.clicked.connect(previous_song)
        self._player.playingChanged.connect(toggle_icon)
        toggle.clicked.connect(toggle_play_state)
        next.clicked.connect(next_song)
        stop.clicked.connect(stop_play)
        self._player.durationChanged.connect(set_progress_length)
        self._player.positionChanged.connect(set_slider_position)
        progress_slider.sliderMoved.connect(self._player.setPosition)

    def set_volume(self, volume: int) -> None:
        """ set volume.

        :param volume: volume value
        """

        self._audio_output.setVolume(volume)

    def set_mode(self, mode: Optional[PlayMode]) -> None:
        """ set play mode.

        :param mode: play mode
        """

        self._play_mode = mode

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
        self._current_media = song
        self._player.setSource(source)
        self._player.play()

    def extend_play_list(self, *songs: Template.Song) -> None:
        """ extend songs to play list.

        :param songs: songs to extend
        """

        self._play_list.extend(songs)
