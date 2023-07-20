import asyncio
import sys
from typing import Optional
from PySide6.QtCore import QBuffer, QIODeviceBase, QSize

from aiohttp import request
from music_api import kg, kw, mg, qianqian, wyy
from music_api._template import Template
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QStyleFactory,
    QWidget,
)
from qasync import QEventLoop, asyncClose, asyncSlot

from .ui.main_ui import Ui_App
from .lib.qt_components import SongLable
from .lib.media_player import Player
from .utils import load_icon

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
        super().__init__(parent)
        self._apis: dict[str, Template] = APIDict()
        self._player = Player(self)
        self._loop.call_soon(
            lambda: (
                self.setupUi(),
                self.connect_to_media_player(),
            )
        )

    def setupUi(self) -> None:
        """ setup Ui."""

        super().setupUi(self)
        self.api_comboBox.addItems([api.name for api in apis])

    def deinit(self) -> None:
        """ destructor."""

        for api in self._apis.values():
            asyncClose(api.deinit)()

    def connect_to_media_player(self) -> None:
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

    @asyncSlot()
    async def on_search_pushButton_clicked(self):
        """ search button callback."""

        async def clear_items(items: list) -> None:
            for item in items:
                if item.widget():
                    item.widget().deleteLater()
                self.result_verticalLayout.removeItem(item)
                await asyncio.sleep(0)

        async def create_item(song_info: Template.SongInfo) -> QWidget:
            widget = QWidget()
            button = QCheckBox("")
            label = SongLable(song_info)
            if song_info.img_url:
                async with request("GET", song_info.img_url) as res:
                    data = await res.read()
                img = QPixmap()
                img.loadFromData(data)
                img = img.scaled(QSize(300, 300))
                buf = QBuffer()
                buf.open(QIODeviceBase.OpenModeFlag.WriteOnly)
                img.save(buf, "JPEG")
                data = buf.data().toBase64().data()
                label.setToolTip(f'<img src="data:image/jpeg;base64,{data.decode()}>')
            hbox = QHBoxLayout(widget)
            hbox.addWidget(button)
            hbox.addWidget(label)
            hbox.addSpacerItem(QSpacerItem(
                40,
                20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            ))
            return widget

        name = self.api_comboBox.currentText()
        api = self._apis[name]
        keyword = self.search_lineEdit.text()
        if not keyword:
            return

        res = await api.search(keyword)
        item_count = self.result_verticalLayout.count()
        if item_count > 0:
            items = [self.result_verticalLayout.itemAt(i) for i in range(item_count)]
            self._loop.create_task(clear_items(items))
        tasks = [self._loop.create_task(create_item(item)) for item in res]
        for task in tasks:
            self.result_verticalLayout.addWidget(await task)


def run() -> None:
    """ run an application."""

    App().run()
