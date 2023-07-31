import asyncio
import sys
from typing import Optional

from music_api import kg, kw, mg, qianqian, wyy
from music_api._template import Template
from PySide6.QtCore import Slot
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QStackedLayout,
    QStyleFactory,
    QWidget,
)
from qasync import QEventLoop, asyncClose, asyncSlot

from ..lib.media_player import Player, PlayMode
from ..ui.main_ui import Ui_App
from ..utils import load_icon
from .home import HomeWidget
from .login import LoginDialog
from .play_list import PlayListWidget
from .search import SearchWidget

apis = (wyy, kw, mg, kg, qianqian)


class APIDict(dict):
    def __missing__(self, key: str) -> Template:
        for api in apis:
            if api.name == key:
                self[key] = api.API()
                return self[key]
        raise KeyError(f"unexpected key: {key}")


class App(QWidget, Ui_App):
    """ Application."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """ initialize.

        :parent parent: parent widget
        """

        self._qt_app = QApplication(sys.argv)
        self._qt_app.setStyle(QStyleFactory.create("Fusion"))
        self._loop = QEventLoop(self._qt_app)
        asyncio.set_event_loop(self._loop)
        super().__init__(parent)
        self._apis: dict[str, Template] = APIDict()
        self._player = Player(self)
        self._login_dialog = LoginDialog(self)
        self._loop.call_soon(
            lambda: (
                self.setupUi(),
                self._connect_to_media_player(),
            )
        )

    def setupUi(self) -> None:
        """ setup Ui."""

        super().setupUi(self)
        self._login_dialog.setupUi()
        self.api_comboBox.addItems([api.name for api in apis])
        self.stack_layout = QStackedLayout(self.main_widget)
        self.home_widget = HomeWidget()
        self.search_widget = SearchWidget()
        self.play_list_widget = PlayListWidget()
        self.play_list_widget.connect_to_player(self._player)
        self.stack_layout.addWidget(self.home_widget)
        self.stack_layout.addWidget(self.search_widget)
        self.stack_layout.addWidget(self.play_list_widget)

    def deinit(self) -> None:
        """ destructor."""

        for api in self._apis.values():
            asyncClose(api.deinit)()

    def _connect_to_media_player(self) -> None:
        """ connect to media player."""

        song_length = 0
        play_icon = load_icon(u":pic/icons/play.png")
        pause_icon = load_icon(u":pic/icons/pause.png")
        sound_on_icon = load_icon(u":pic/icons/sound_on.png")
        sound_off_icon = load_icon(u":pic/icons/sound_off.png")

        def toggle_play_icon() -> None:
            if self._player.is_playing():
                self.toggle_play_state_pushButton.setToolTip("<b>播放</b>")
                self.toggle_play_state_pushButton.setIcon(play_icon)
            else:
                self.toggle_play_state_pushButton.setToolTip("<b>暂停</b>")
                self.toggle_play_state_pushButton.setIcon(pause_icon)

        def toggle_play_state() -> None:
            if not self._player.has_source():
                return
            if self._player.is_playing():
                self._player.pause()
            else:
                self._player.play()

        def do_when_media_status_changed(status: QMediaPlayer.MediaStatus) -> None:
            if status is status.EndOfMedia:
                self._player.schedule()
            elif status is status.InvalidMedia:
                QMessageBox.warning(self, "warning", "invalid media")

        def stop_play() -> None:
            self._player.stop()
            self.progress_Slider.setEnabled(False)
            self.progress_label.setText("00 / 00")

        def format_song_length(length: int) -> str:
            seconds = length / 1000
            minitus = int(seconds // 60)
            return f"{minitus:0>2}:{int(seconds - minitus * 60):0>2}"

        def set_progress_length(length: int) -> None:
            nonlocal song_length
            if length > 0:
                song_length = format_song_length(length)
                self.progress_Slider.setEnabled(True)
                self.progress_Slider.setRange(0, length)
                self.progress_label.setText(f"00 / {song_length}")
            else:
                self.progress_label.setText("00 / 00")

        def set_progress_slider_position(pos: int) -> None:
            self.progress_Slider.setSliderPosition(pos)
            self.progress_label.setText(f"{format_song_length(pos)} / {song_length}")

        def toggle_muted_icon() -> None:
            if self._player.is_muted():
                self.volume_pushButton.setToolTip("<b>已静音</b>")
                self.volume_pushButton.setIcon(sound_off_icon)
                self.volume_Slider.setEnabled(False)
            else:
                self.volume_pushButton.setToolTip("<b>音量</b>")
                self.volume_pushButton.setIcon(sound_on_icon)
                self.volume_Slider.setEnabled(True)

        def toggle_muted() -> None:
            is_not_muted = not self._player.is_muted()
            self._player.set_muted(is_not_muted)

        def set_volume(volume: int) -> None:
            self.volume_Slider.setToolTip(f"<b>{volume}</b>")
            self._player.set_volume(volume)

        self.previous_song_pushButton.clicked.connect(self._player.previous)
        self._player.playingChanged.connect(toggle_play_icon)
        self._player.mediaStatusChanged.connect(do_when_media_status_changed)
        self.toggle_play_state_pushButton.clicked.connect(toggle_play_state)
        self.next_song_pushButton.clicked.connect(self._player.next)
        self.stop_play_pushButton.clicked.connect(stop_play)
        self._player.durationChanged.connect(set_progress_length)
        self._player.positionChanged.connect(set_progress_slider_position)
        self.progress_Slider.sliderMoved.connect(self._player.set_position)
        self._player.mutedChanged.connect(toggle_muted_icon)
        self.volume_pushButton.clicked.connect(toggle_muted)
        self.volume_Slider.valueChanged.connect(set_volume)

        self.volume_Slider.setSliderPosition(50)

    def run(self) -> None:
        """ run Application."""

        async def _run() -> None:
            fut = self._loop.create_future()
            self._qt_app.aboutToQuit.connect(
                lambda: (
                    self.deinit(),
                    fut.cancel()
                )
            )
            self.show()
            try:
                await fut
            except asyncio.CancelledError:
                pass
        self._loop.run_until_complete(_run())
        to_cancel = asyncio.tasks.all_tasks(self._loop)
        if to_cancel:
            for task in to_cancel:
                task.cancel()
            asyncio.gather(*to_cancel, return_exceptions=True)
        self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        self._loop.run_until_complete(self._loop.shutdown_default_executor())

    @asyncSlot()
    async def on_search_pushButton_clicked(self):
        """ search button callback."""

        name = self.api_comboBox.currentText()
        api = self._apis[name]
        keyword = self.search_lineEdit.text()
        if not keyword:
            return

        self.stack_layout.setCurrentIndex(1)
        res = await api.search(keyword)
        self.search_widget.clear()
        self.search_widget.show_items(res)

    @Slot()
    def on_home_pushButton_clicked(self) -> None:
        self.stack_layout.setCurrentIndex(0)

    @Slot()
    def on_switch_to_search_page_pushButton_clicked(self) -> None:
        self.stack_layout.setCurrentIndex(1)

    @Slot()
    def on_switch_to_list_page_pushButton_clicked(self) -> None:
        self.stack_layout.setCurrentIndex(2)

    @asyncSlot()
    async def on_login_pushButton_clicked(self) -> None:
        name = self.api_comboBox.currentText()
        if name not in self._apis:
            api = self._apis[name]
            await asyncio.sleep(0.5)
        else:
            api = self._apis[name]
        if api.login.QR is None and api.login.SMS is None and api.login.PWD is None:
            QMessageBox.information(self, "info", "current API do not support log in")
            return

        self._login_dialog.connect_to_api(api)
        self._login_dialog.show()

    @Slot(int)
    def on_playback_rate_comboBox_currentIndexChanged(self, index: int) -> None:
        _ = index
        rate = float(self.playback_rate_comboBox.currentText())
        self._player.set_playback_rate(rate)

    @Slot(int)
    def on_play_mode_comboBox_currentIndexChanged(self, index: int) -> None:
        self._player.set_mode(
            PlayMode(index) if self.play_mode_comboBox.currentText() else None
        )


def run() -> None:
    """ run an application."""

    App().run()
