from functools import partial
from enum import IntEnum
import tkinter as tk
import tkinter.ttk as ttk

from ..sources.model import LoginConfig
from ..lib import asynctk


class LoginToplevel(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.notebook = ttk.Notebook(self)
        self.frame9 = ttk.Frame(self.notebook)
        self.label4 = ttk.Label(self.frame9)
        self.label4.configure(text="账号")
        self.label4.grid(column=0, ipadx=3, ipady=3, padx=20, pady=9, row=0)
        self.label5 = ttk.Label(self.frame9)
        self.label5.configure(text="密码")
        self.label5.grid(column=0, ipadx=3, ipady=3, padx=20, pady=9, row=1)
        self.id_entry = ttk.Entry(self.frame9)
        self.id_entry.configure(width=30)
        self.id_entry.grid(column=1, columnspan=4, ipadx=3, ipady=3, row=0, sticky="w")
        self.password_entry = ttk.Entry(self.frame9)
        self.password_entry.configure(show="★", width=30)
        self.password_entry.grid(
            column=1, columnspan=4, ipadx=3, ipady=3, row=1, sticky="w"
        )
        self.label6 = ttk.Label(self.frame9)
        self.label6.configure(text="验证码")
        self.label6.grid(column=0, ipadx=3, ipady=3, padx=20, pady=9, row=2)
        self.verify_entry = ttk.Entry(self.frame9)
        self.verify_entry.configure(state="disabled", width=10)
        self.verify_entry.grid(column=1, ipadx=3, ipady=3, row=2, sticky="w")
        self.verify_label = tk.Label(self.frame9)
        self.verify_label.configure(bitmap="gray12", height=30, width=60)
        self.verify_label.grid(column=2, columnspan=3, row=2, sticky="w")
        self.visible_checkbutton = ttk.Checkbutton(self.frame9)
        self.__pwd_visible = tk.IntVar(value="")
        self.visible_checkbutton.configure(text="密码可见", variable=self.__pwd_visible)
        self.visible_checkbutton.grid(column=4, row=3, sticky="e")
        self.visible_checkbutton.configure(command=self.__toggle_pwd_visible)
        self.frame9.configure(height=200, width=200)
        self.frame9.pack(side="top")
        self.notebook.add(self.frame9, text="账号密码登录")
        self.frame1 = ttk.Frame(self.notebook)
        self.qr_code_label = tk.Label(self.frame1)
        self.qr_code_label.configure(bitmap="gray25", height=120, width=120)
        self.qr_code_label.pack(anchor="center", expand="true", side="top")
        self.frame1.configure(height=200, width=200)
        self.frame1.pack(side="top")
        self.notebook.add(self.frame1, text="二维码登录")
        self.frame4 = ttk.Frame(self.notebook)
        self.label3 = ttk.Label(self.frame4)
        self.label3.configure(text="手机号码")
        self.label3.grid(column=0, ipadx=3, ipady=3, padx=20, pady=9, row=0)
        self.label7 = ttk.Label(self.frame4)
        self.label7.configure(text="验证码")
        self.label7.grid(column=0, ipadx=3, ipady=3, padx=20, pady=9, row=1)
        self.phone_entry = ttk.Entry(self.frame4)
        self.phone_entry.configure(width=30)
        self.phone_entry.grid(
            column=1, columnspan=4, ipadx=3, ipady=3, pady=30, row=0, sticky="w"
        )
        self.sms_verify_entry = ttk.Entry(self.frame4)
        self.sms_verify_entry.configure(width=10)
        self.sms_verify_entry.grid(
            column=1, columnspan=2, ipadx=3, ipady=3, row=1, sticky="w"
        )
        self.sms_button = ttk.Button(self.frame4)
        self.sms_button.configure(text="点击发送验证码")
        self.sms_button.grid(column=3, columnspan=2, row=1)
        self.frame4.configure(height=200, width=200)
        self.frame4.pack(side="top")
        self.notebook.add(self.frame4, text="短信验证登录")
        self.notebook.configure(height=160, width=330)
        self.notebook.grid(column=0, columnspan=5, row=0)
        self.message_label = ttk.Label(self)
        self.message_label.configure(anchor="center", font="{微软雅黑} 12 {}")
        self.message_label.grid(column=0, columnspan=5, row=1)
        self.cancel_button = ttk.Button(self)
        self.cancel_button.configure(text="取消", width=6)
        self.cancel_button.grid(column=1, pady=6, row=2)
        self.accept_button = ttk.Button(self)
        self.accept_button.configure(text="确定", width=6)
        self.accept_button.grid(column=4, pady=6, row=2)
        self.configure(height=200, width=200)
        self.resizable(False, False)
        self.title("login")

    def __toggle_pwd_visible(self) -> None:
        state = self.__pwd_visible.get()
        self.password_entry.configure(show='' if state else '★')


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


if __name__ == "__main__":
    app = tk.Tk()
    dialog = LoginDialog(app)

    btn = tk.Button(app, text="show dialog", command=dialog.show)
    btn.pack()
    btn = tk.Button(app, text='destroy', command=dialog.destroy)
    btn.pack()
    tk.Button(app, text='visible tab1', command=lambda : print(dialog.visible(dialog.PWD))).pack()

    app.mainloop()
