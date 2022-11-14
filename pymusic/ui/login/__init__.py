from enum import IntEnum
from functools import partial
import tkinter as tk

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
        self.__parsers = [self.PWD_info, NotImplemented, NotImplemented]
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

    def __accept_callback(self) -> None:
        """接受事件."""

        def login_callback(fut):
            res = fut.result()
            if res != 0:
                self.log(res or '账号格式不正确')
            else:
                self.close()

        for tab in LoginType:
            tab_id = tab.value
            if self.visible(tab_id):
                callback, parser = self.__callbacks[tab_id]
                info = parser()
                if info is not None:
                    self.log('登录中......', color='blue')
                    asynctk.create_task(callback(*info)).\
                        add_done_callback(login_callback)
                break

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
        for callback, parser, tab in zip(callbacks, self.__parsers, LoginType):
            tab_id = tab.value
            state = 'hidden'
            if callback is not None:
                assert callable(callback)
                state = 'normal'
                self.__callbacks[tab_id] = (callback, partial(parser, config))
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

    def PWD_info(
        self,
        config: LoginConfig,
    ) -> tuple:
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
        return login_id, password, verify_code

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

        tl = self.__tl
        tl.withdraw()
        tl.message_label.configure(text='')
        self.__master.focus_set()

    def destroy(self) -> None:
        """销毁."""

        self.__tl.destroy()
