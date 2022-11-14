import tkinter as tk
import tkinter.ttk as ttk


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


if __name__ == "__main__":
    pass
