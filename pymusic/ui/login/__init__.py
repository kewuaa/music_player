from enum import IntEnum
from functools import partial
from asyncio.futures import Future
from asyncio import iscoroutinefunction
import tkinter as tk

from PIL import ImageTk
from PIL import Image
import qrcode

from pymusic.sources.model import LoginConfig
from pymusic.lib import asynctk
from .dialog import LoginToplevel


class LoginType(IntEnum):
    PWD = 0
    QR = 1
    SMS = 2


class LoginDialog:
    """登录对话框."""

    def __init__(self, master=None) -> None:
        master = master or tk.Tk()
        self.__master = master
        self.__done_befor_close = None
        self.__callbacks = [None] * 3
        self.__init_toplevel()

    def __init_toplevel(self) -> None:
        """初始化toplevel."""

        tl = self.__tl = LoginToplevel(self.__master)
        tl.transient(self.__master)
        tl.withdraw()
        tl.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )
        tl.cancel_button.configure(command=self.close)
        tl.accept_button.configure(command=self.__accept_callback)
        tl.notebook.enable_traversal()

    def __center_window(self):
        """Center a window on its parent or screen."""

        window = self.__tl
        height = window.winfo_height()
        width = window.winfo_width()
        master = self.__master
        if master:
            x_coord = int(
                master.winfo_x() + (master.winfo_width() / 2 - width / 2)
            )
            y_coord = int(
                master.winfo_y() + (master.winfo_height() / 2 - height / 2)
            )
        else:
            x_coord = int(window.winfo_screenwidth() / 2 - width / 2)
            y_coord = int(window.winfo_screenheight() / 2 - height / 2)
        geom = "{0}x{1}+{2}+{3}".format(width, height, x_coord, y_coord)
        window.geometry(geom)

    def __run(self) -> None:
        """运行."""

        self.__center_window()
        tl = self.__tl
        tl.deiconify()
        tl.wait_visibility()
        initial_focus = tl.focus_lastfor()
        if initial_focus:
            initial_focus.focus_set()

    def __login_callback(self, fut: Future):
        exception = fut.exception()
        if exception is not None:
            print('[ERROR]:', exception)
            self.log(str(exception) or 'unknown error')
        else:
            self.log('登陆成功', color='blue')
            self.__tl.after(100, self.close)

    def __accept_callback(self) -> None:
        """接受事件."""

        for tab in LoginType:
            tab_id = tab.value
            if self.visible(tab_id):
                callback = self.__callbacks[tab_id]
                assert callable(callback)
                self.__tl.message_label.configure(text='')
                task: Future = callback()
                if task is not None:
                    task.add_done_callback(self.__login_callback)
                break

    def __toggle_bind(self, fetch_img) -> None:
        """切换tab触发事件."""

        def create_task() -> None:
            nonlocal task
            task = loop.create_task(fetch_img(self.__login_callback))
            task.add_done_callback(self.__update_qrcode)

        def func(event: tk.Event):
            try:
                tab_id = notebook.index('current')
            except tk.TclError:
                return
            nonlocal task
            if tab_id == LoginType.QR:
                self.__tl.accept_button.grid_remove()
                loop.call_soon_threadsafe(create_task)
            else:
                self.__tl.accept_button.grid()
                if task is not None:
                    if hasattr(task, '_special_callback'):
                        asynctk.call_soon(task._special_callback)
                    task = None

        task: Future = None
        self.__done_befor_close = lambda: \
            task._special_callback() \
            if task is not None and hasattr(task, '_special_callback') \
            else None
        loop = asynctk._callback_loop
        notebook = self.__tl.notebook
        notebook.unbind_all('<<NotebookTabChanged>>')
        notebook.bind('<<NotebookTabChanged>>', func)

    def __update_qrcode(self, fut: Future) -> None:
        exception = fut.exception()
        if exception is not None:
            self.log(str(exception) or 'unknow error')
            return
        qrimg = fut.result()
        if type(qrimg) is str:
            scan_url = qrimg
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(scan_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
        else:
            img = qrimg
        qr_label = self.__tl.qr_code_label
        size = int(qr_label.winfo_width() / 1.5), \
            int(qr_label.winfo_height() / 1.5)
        img = img.resize(size, Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        qr_label.configure(image=img)
        qr_label.img = img

    def __bind_sms_func(self, func) -> None:
        def command():
            cellphone = self.__tl.phone_entry.get().strip()
            if not cellphone:
                self.log('请输入电话号码')
                return
            else:
                s = set(cellphone)
                if len(cellphone) != 11 or len(s | set('0123456789')) > 10:
                    self.log('请输入正确的电话号码')
                    return
            asynctk.create_task(
                func(cellphone),
            ).add_done_callback(lambda fut: self.log(
                fut.exception() or '验证码已发送',
                color='blue' if fut.exception() is None else 'red',
            ))
        assert iscoroutinefunction(func)
        self.__tl.sms_button.configure(command=command)

    def reset(
        self,
        config: LoginConfig,
    ) -> None:
        """重置."""

        tl = self.__tl
        notebook = tl.notebook
        tl.verify_entry.configure(
            state='normal' if config.need_verify else 'disabled',
        )
        callbacks = (
            config.PWD_callback,
            config.QR_callback,
            config.SMS_callback,
        )
        for callback, login_type in zip(callbacks, LoginType):
            tab_id = login_type.value
            state = 'hidden'
            if callback is not None:
                state = 'normal'
                if login_type is LoginType.PWD:
                    self.__callbacks[tab_id] = partial(
                        self.__PWD_callback,
                        config,
                        callback,
                    )
                elif login_type is LoginType.QR:
                    self.__toggle_bind(callback)
                elif login_type is LoginType.SMS:
                    send_sms, login = callback()
                    self.__bind_sms_func(send_sms)
                    self.__callbacks[tab_id] = partial(
                        self.__SMS_callback,
                        config,
                        login,
                    )
            notebook.tab(tab_id, state=state)

    def visible(self, tab_id: int) -> bool:
        notebook = self.__tl.notebook
        tab_name = notebook.tabs()[tab_id]
        frame: tk.Frame = self.__master.nametowidget(tab_name)
        return frame.winfo_ismapped()

    def update_pwd(self, config: dict) -> None:
        tl = self.__tl
        tl.id_entry.delete(0, 'end')
        tl.id_entry.insert(0, config.get('login_id', ''))
        tl.password_entry.delete(0, 'end')
        tl.password_entry.insert(0, config.get('password', ''))

    def __PWD_callback(self, config: LoginConfig, callback) -> Future | None:
        tl = self.__tl
        need_verify = config.need_verify
        login_id = tl.id_entry.get().strip()
        password = tl.password_entry.get()
        verify_code = tl.verify_entry.get().strip()
        if not login_id:
            self.log('请输入账号')
            return
        if config.check_id:
            s = set(login_id)
            if len(s | set('0123456789')) > 10:
                self.log('账号不能包含非数字字符')
                return
        if not password:
            self.log('请输入密码')
            return
        if need_verify and not verify_code:
            self.log('请输入验证码')
            return
        return asynctk.create_task(callback(login_id, password, verify_code))

    def __SMS_callback(self, config: LoginConfig, callback) -> Future | None:
        tl = self.__tl
        cellphone = tl.phone_entry.get().strip()
        verify_code = tl.sms_verify_entry.get().strip()
        if not cellphone:
            self.log('请输入电话号码')
            return
        else:
            s = set(cellphone)
            if len(cellphone) != 11 or len(s | set('0123456789')) > 10:
                self.log('请输入正确的电话号码')
                return
        if not verify_code:
            self.log('请输入短信验证码')
            return
        return asynctk.create_task(callback(cellphone, verify_code))

    def log(self, msg, color: str = None) -> None:
        """打印消息."""

        self.__tl.message_label.configure(
            text=msg,
            foreground=color or 'red',
        )

    def show(self) -> None:
        """显示."""

        self.__run()

    def close(self) -> None:
        """关闭."""

        if self.__done_befor_close is not None:
            self.__done_befor_close()
        tl = self.__tl
        tl.withdraw()
        tl.message_label.configure(text='')
        self.__master.focus_set()

    def destroy(self) -> None:
        """销毁."""

        if self.__done_befor_close is not None:
            self.__done_befor_close()
        self.__tl.destroy()
