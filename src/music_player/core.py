import asyncio
import sys
from functools import partial
from typing import Callable, Optional

from aiohttp import request
from music_api import kg, kw, mg, qianqian, wyy
from music_api._template import Template
from PySide6.QtCore import QBuffer, QIODeviceBase, QSize, Slot
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QStyleFactory,
    QWidget,
)
from qasync import QEventLoop, asyncClose, asyncSlot

from .lib.media_player import Player
from .lib.qt_components import SongLable
from .ui.login_ui import Ui_Dialog
from .ui.main_ui import Ui_App
from .utils import load_icon

apis = (wyy, kw, mg, kg, qianqian)


class APIDict(dict):
    def __missing__(self, key: str) -> Template:
        for api in apis:
            if api.name == key:
                self[key] = api.API()
                return self[key]
        raise KeyError(f"unexpected key: {key}")


class LoginDialog(QDialog, Ui_Dialog):
    """ log in dialog."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        loop: Optional[asyncio.base_events.BaseEventLoop] = None
    ) -> None:
        """ initialize.

        :parent: parent widget
        """

        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._api: Optional[Template] = None
        self._wait_for_scan_task: Optional[asyncio.Task] = None
        self._accept: Callable[[], None] = lambda: None
        super().__init__(parent)

    def setupUi(self):
        return super().setupUi(self)

    def _clear_edit(self) -> None:
        line_edits = (
            self.cellphone_lineEdit,
            self.sms_captcha_lineEdit,
            self.verify_code_lineEdit,
            self.login_id_lineEdit,
            self.pwd_captcha_lineEdit,
            self.password_lineEdit,
        )
        for edit in line_edits:
            edit.clear()

    def _cancel_tasks(self) -> None:
        """ cancel all tasks."""

        if self._wait_for_scan_task is not None:
            self._wait_for_scan_task.cancel()
            self._wait_for_scan_task = None

    def _success_callback(self, fut: asyncio.Task) -> None:
        """ callback function called when successfully login."""

        if fut.cancelled():
            return
        exception = fut.exception()
        if exception is not None:
            QMessageBox.warning(self, "warning", str(exception))
            return
        self._cancel_tasks()
        self._loop.call_soon(
            QMessageBox.information,
            self, "info", "successfully log in"
        )
        super().accept()

    def _display_img_on_label(self, img: bytes, label: QLabel) -> None:
        """ display image on label.

        :param img: image bytes
        :param label: label to display image
        """

        pixmap = QPixmap()
        pixmap.loadFromData(img)
        size = label.size()
        pixmap = pixmap.scaled(size)
        label.setPixmap(pixmap)

    async def _show_qrcode(self, qrcode: bytes) -> None:
        """ show qr code.

        :param img: qr code bytes
        """

        self._display_img_on_label(qrcode, self.QR_label)

    def _display_captcha_callback(self, fut: asyncio.Task, label: QLabel) -> None:
        """ callback function to display captcha.

        :param label: label to display
        """

        exception = fut.exception()
        if exception is not None:
            QMessageBox.warning(self, "warning", str(exception))
            return
        self._display_img_on_label(fut.result(), label)
        self.refresh_pwd_captcha_pushButton

    @Slot()
    def on_refresh_sms_captcha_pushButton_clicked(self) -> None:
        assert self._api is not None
        assert self._api.login.SMS is not None
        assert self._api.login.SMS[0] is not None
        self._loop.create_task(self._api.login.SMS[0]()) \
            .add_done_callback(
                partial(self._display_captcha_callback, label=self.sms_captcha_label)
            )

    @Slot()
    def on_refresh_pwd_captcha_pushButton_clicked(self) -> None:
        assert self._api is not None
        assert self._api.login.PWD is not None
        assert self._api.login.PWD[0] is not None
        self._loop.create_task(self._api.login.PWD[0]()) \
            .add_done_callback(
                partial(self._display_captcha_callback, label=self.pwd_captcha_label)
        )

    @Slot()
    def on_send_sms_pushButton_clicked(self) -> None:
        assert self._api is not None
        assert self._api.login.SMS is not None
        cellphone = self.cellphone_lineEdit.text()
        if not cellphone:
            return
        captcha = ""
        if self.sms_captcha_frame.isEnabled():
            captcha = self.sms_captcha_lineEdit.text()
            if not captcha:
                return
        self._loop.create_task(self._api.login.SMS[1](cellphone, captcha))

    @Slot(int)
    def on_tabWidget_currentChanged(self, index: int) -> None:
        if index < 0:
            return
        elif index == 0:
            self._accept = lambda: None
        elif index == 1:
            self._accept = self._accept_SMS
        elif index == 2:
            self._accept = self._accept_PWD

    def connect_to_api(self, api: Template) -> None:
        """ connect to api.

        :param api: API
        """

        if self._api is not api:
            self._clear_edit()
            self._api = api

        index_setted = False
        if api.login.QR is None:
            self.tabWidget.setTabEnabled(0, False)
        else:
            if not index_setted:
                self.tabWidget.setCurrentIndex(0)
                index_setted = True
            self.tabWidget.setTabEnabled(0, True)
            login_by_qrcode = api.login.QR
            self._wait_for_scan_task = self._loop.create_task(
                login_by_qrcode(self._show_qrcode)
            )
            self._wait_for_scan_task.add_done_callback(self._success_callback)

        if api.login.SMS is None:
            self.tabWidget.setTabEnabled(1, False)
        else:
            if not index_setted:
                self.tabWidget.setCurrentIndex(1)
                index_setted = True
            self.tabWidget.setTabEnabled(1, True)
            fetch_captcha, *_ = api.login.SMS
            if fetch_captcha is None:
                self.sms_captcha_frame.setEnabled(False)
            else:
                self.sms_captcha_frame.setEnabled(True)
                self._loop.create_task(fetch_captcha()).add_done_callback(
                    partial(
                        self._display_captcha_callback,
                        label=self.sms_captcha_label
                    )
                )

        if api.login.PWD is None:
            self.tabWidget.setTabEnabled(2, False)
        else:
            if not index_setted:
                self.tabWidget.setCurrentIndex(2)
                index_setted = True
            self.tabWidget.setTabEnabled(2, True)
            fetch_captcha, *_ = api.login.PWD
            if fetch_captcha is None:
                self.pwd_captcha_frame.setEnabled(False)
            else:
                self.pwd_captcha_frame.setEnabled(True)
                self._loop.create_task(fetch_captcha()).add_done_callback(
                    partial(
                        self._display_captcha_callback,
                        label=self.pwd_captcha_label
                    )
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        self._cancel_tasks()
        return super().closeEvent(event)

    def _accept_SMS(self) -> None:
        """ accept when SMS."""

        assert self._api is not None
        assert self._api.login.SMS is not None
        cellphone = self.cellphone_lineEdit.text()
        if not cellphone:
            QMessageBox.information(self, "info", "empty cellphone")
            return
        captcha = ""
        if self.sms_captcha_frame.isEnabled():
            captcha = self.sms_captcha_lineEdit.text()
            if not captcha:
                QMessageBox.information(self, "info", "empty captcha")
                return
        verify_code = self.verify_code_lineEdit.text()
        if not verify_code:
            QMessageBox.information(self, "info", "empty verify code")
            return
        self._loop.create_task(
            self._api.login.SMS[-1](cellphone, verify_code, captcha)
        ).add_done_callback(self._success_callback)

    def _accept_PWD(self) -> None:
        """ accept when PWD."""

        assert self._api is not None
        assert self._api.login.PWD is not None
        login_id = self.login_id_lineEdit.text()
        if not login_id:
            QMessageBox.information(self, "info", "empty log in ID")
            return
        captcha = ""
        if self.pwd_captcha_frame.isEnabled():
            captcha = self.pwd_captcha_lineEdit.text()
            if not captcha:
                QMessageBox.information(self, "info", "empty captcha")
                return
        password = self.password_lineEdit.text()
        if not password:
            QMessageBox.information(self, "info", "empty password")
            return
        self._loop.create_task(
            self._api.login.PWD[-1](login_id, password, captcha)
        ).add_done_callback(self._success_callback)

    def accept(self) -> None:
        self._accept()

    def reject(self) -> None:
        self._cancel_tasks()
        return super().reject()


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

    @asyncSlot()
    async def on_login_pushButton_clicked(self) -> None:
        """ log in."""

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


def run() -> None:
    """ run an application."""

    App().run()
