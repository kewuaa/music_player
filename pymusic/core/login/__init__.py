from enum import IntEnum
from functools import partial
from asyncio.futures import Future
from asyncio import iscoroutinefunction
import tkinter as tk

from PIL import ImageTk
from PIL import Image
import qrcode

from pymusic.sources.model import LoginConfig
from pymusic.ui.login import LoginToplevel
from pymusic.lib.logger import logger
from pymusic.lib import asynctk


class LoginType(IntEnum):
    PWD = 0
    QR = 1
    SMS = 2


class LoginDialog:
    """登录对话框."""

    def __init__(self, master=None) -> None:
        master = master or tk.Tk()
        self.__master = master
        self.__done_befor_close = set()
        self.__accept_callbacks = [None] * 3
        self.__toggle_callbacks = [None] * 3
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
        tl.notebook.bind('<<NotebookTabChanged>>', self.__toggle_callback)
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

    def visible(self, tab_id: int) -> bool:
        notebook = self.__tl.notebook
        tab_name = notebook.tabs()[tab_id]
        frame: tk.Frame = self.__master.nametowidget(tab_name)
        return frame.winfo_ismapped()

    def __parse_img(self, source) -> Image:
        if type(source) is str:
            scan_url = source
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
            img = source
        return img

    def __refresh_img(self, label_type: LoginType, source) -> None:
        tl = self.__tl
        label = (
            tl.verify_label,
            tl.qr_code_label,
            tl.sms_verify_label,
        )[label_type.value]
        img = self.__parse_img(source)
        size = int(label.winfo_width() / 1.5), \
            int(label.winfo_height() / 1.5)
        img = img.resize(size, Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        label.configure(image=img)
        label.img = img

    def __login_callback(self, fut: Future):
        exception = fut.exception()
        if exception is not None:
            logger.error(exception)
            self.log(str(exception) or 'unknown error')
        else:
            self.log('登陆成功', color='blue')
            self.__tl.after(100, self.close)

    def __accept_callback(self) -> None:
        """接受事件."""

        notebook = self.__tl.notebook
        tab_id = notebook.index('current')
        callback = self.__accept_callbacks[tab_id]
        self.__tl.message_label.configure(text='')
        task: Future = callback()
        if task is not None:
            task.add_done_callback(self.__login_callback)

    def __toggle_callback(self, event: tk.Event) -> None:
        notebook = self.__tl.notebook
        try:
            tab_id = notebook.index('current')
        except tk.TclError:
            return
        self.__tl.message_label.configure(text='')
        if tab_id == LoginType.QR:
            self.__tl.accept_button.grid_remove()
        else:
            self.__tl.accept_button.grid()
        callback = self.__toggle_callbacks[tab_id]
        callback is not None and callback()

    def __QR_callback(self, fetch_img):
        """切换tab触发事件."""

        def create_task() -> None:
            nonlocal task
            task = loop.create_task(fetch_img(self.__login_callback))
            task.add_done_callback(self.__update_qrcode)

        def callback():
            nonlocal callback_funcid
            loop.call_soon_threadsafe(create_task)
            callback_funcid = notebook.bind(
                '<<NotebookTabChanged>>',
                cancel_callback,
                add='+',
            )
            self.__done_befor_close.add(cancel_task)

        def cancel_task():
            if hasattr(task, '_special_callback'):
                task._special_callback()
                self.__done_befor_close.discard(cancel_task)

        def cancel_callback(event: tk.Event) -> None:
            try:
                tab_id = notebook.index('current')
            except tk.TclError:
                return
            if tab_id != LoginType.QR:
                cancel_task()
                notebook.unbind('<<NotebookTabChanged>>', callback_funcid)

        task: Future = None
        loop = asynctk._callback_loop
        notebook = self.__tl.notebook
        callback_funcid = None
        return callback

    def __update_qrcode(self, fut: Future) -> None:
        exception = fut.exception()
        if exception is not None:
            logger.error(exception)
            self.log(str(exception) or 'unknow error')
            return
        source = fut.result()
        self.__refresh_img(LoginType.QR, source)

    def __PWD_callback(
        self,
        check_id: bool,
        callback,
    ) -> Future | None:
        tl = self.__tl
        login_id = tl.id_entry.get().strip()
        password = tl.password_entry.get()
        verify_code = tl.verify_entry.get().strip() \
            if str(tl.verify_entry['state']) == 'normal' else None
        need_verify = verify_code is not None
        if not login_id:
            self.log('请输入账号')
            return
        if check_id:
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
        args = [login_id, password]
        if verify_code:
            args.append(verify_code)
        return asynctk.create_task(callback(*args))

    def update_login_info(self, config: dict) -> None:
        tl = self.__tl
        tl.id_entry.insert(0, config.get('login_id', ''))
        tl.password_entry.insert(0, config.get('password', ''))
        tl.cellphone_entry.insert(0, config.get('cellphone', ''))

    def __SMS_callback(self, callback) -> Future | None:
        tl = self.__tl
        cellphone = tl.cellphone_entry.get().strip()
        sms_code = tl.sms_code_entry.get().strip()
        verify_code = tl.sms_verify_entry.get().strip() \
            if str(tl.sms_verify_entry['state']) == 'normal' else None
        need_verify = verify_code is not None
        if not cellphone:
            self.log('请输入电话号码')
            return
        else:
            s = set(cellphone)
            if len(cellphone) != 11 or len(s | set('0123456789')) > 10:
                self.log('请输入正确的电话号码')
                return
        if not sms_code:
            self.log('请输入短信验证码')
            return
        if need_verify and not verify_code:
            self.log('请输入图形验证码')
            return
        args = [cellphone, sms_code]
        if verify_code:
            args.append(verify_code)
        return asynctk.create_task(callback(*args))

    def __bind_sms_func(self, func) -> None:
        def command():
            cellphone = self.__tl.cellphone_entry.get().strip()
            verify_code = sms_verify_entry.get().strip() \
                if str(sms_verify_entry['state']) == 'normal' else None
            need_verify = verify_code is not None
            if not cellphone:
                self.log('请输入电话号码')
                return
            else:
                s = set(cellphone)
                if len(cellphone) != 11 or len(s | set('0123456789')) > 10:
                    self.log('请输入正确的电话号码')
                    return
            if need_verify and not verify_code:
                self.log('请输入图片验证码')
                return
            args = [cellphone]
            if verify_code:
                args.append(verify_code)
            asynctk.create_task(
                func(*args),
            ).add_done_callback(lambda fut: self.log(
                fut.exception() or '验证码已发送',
                color='blue' if fut.exception() is None else 'red',
            ))

        assert iscoroutinefunction(func)
        sms_verify_entry = self.__tl.sms_verify_entry
        self.__tl.sms_button.configure(command=command)

    def __verify(self, login_type: LoginType, fetch_img):
        def refresh_callback(fut: Future):
            exception = fut.exception()
            if exception is not None:
                logger.error(exception)
                raise RuntimeError('unknown error')
            source = fut.result()
            self.__refresh_img(login_type, source)

        def fetch():
            asynctk.create_task(
                fetch_img(),
            ).add_done_callback(refresh_callback)

        fetch()
        return fetch

    def reset(
        self,
        config: LoginConfig,
    ) -> None:
        """重置."""

        def reset_verify(verify, login_type: LoginType):
            label = (
                tl.verify_entry,
                None,
                tl.sms_verify_entry,
            )[login_type.value]
            state = 'disabled'
            if verify:
                state = 'normal'
                self.__toggle_callbacks[login_type.value] = \
                    self.__verify(login_type, verify[0])
            label.configure(state=state)

        tl = self.__tl
        notebook = tl.notebook
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
                    login, *verify = callback
                    reset_verify(verify, LoginType.PWD),
                    self.__accept_callbacks[tab_id] = partial(
                        self.__PWD_callback,
                        config.check_id,
                        login,
                    )
                elif login_type is LoginType.QR:
                    fetch_img, *_ = callback
                    self.__toggle_callbacks[tab_id] = \
                        self.__QR_callback(fetch_img)
                elif login_type is LoginType.SMS:
                    send_sms, login, *verify = callback
                    reset_verify(verify, LoginType.SMS),
                    self.__bind_sms_func(send_sms)
                    self.__accept_callbacks[tab_id] = partial(
                        self.__SMS_callback,
                        login,
                    )
            notebook.tab(tab_id, state=state)

    def log(self, msg, color: str = None) -> None:
        """打印消息."""

        self.__tl.message_label.configure(
            text=msg,
            foreground=color or 'red',
        )

    def __run(self) -> None:
        """运行."""

        self.__center_window()
        tl = self.__tl
        tl.deiconify()
        tl.wait_visibility()
        initial_focus = tl.focus_lastfor()
        if initial_focus:
            initial_focus.focus_set()

    def show(self) -> None:
        """显示."""

        self.__run()

    def __clear(self) -> None:
        tl = self.__tl
        tl.message_label.configure(text='')
        for entry in (
            tl.id_entry,
            tl.password_entry,
            tl.verify_entry,
            tl.cellphone_entry,
            tl.sms_code_entry,
            tl.sms_verify_entry,
        ):
            entry.delete(0, 'end')

    def close(self) -> None:
        """关闭."""

        for func in self.__done_befor_close.copy():
            func()
        self.__clear()
        self.__tl.withdraw()
        self.__master.focus_set()

    def destroy(self) -> None:
        """销毁."""

        self.close()
        self.__tl.destroy()
