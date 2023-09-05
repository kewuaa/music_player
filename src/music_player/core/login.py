import asyncio
from functools import partial
from typing import Callable, Optional

from music_api import Template
from PySide6.QtCore import Slot
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QWidget

from ..ui.login_ui import Ui_Dialog


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
