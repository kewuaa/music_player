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
        self._loop.call_soon(self.setupUi)

    def setupUi(self) -> None:
        """ setup Ui."""

        super().setupUi(self)
        self.api_comboBox.addItems([api.name for api in apis])
        self._player.connect_to_widgets(
            self.previous_song_pushButton,
            self.toggle_play_state_pushButton,
            self.next_song_pushButton,
            self.stop_play_pushButton,
            self.progress_Slider,
            self.progress_label
        )

    def deinit(self) -> None:
        """ destructor."""

        for api in self._apis.values():
            asyncClose(api.deinit)()

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
