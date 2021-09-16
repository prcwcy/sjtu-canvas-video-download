import tkinter as tk
import tkinter.messagebox
from bs4 import BeautifulSoup
from PIL import ImageTk
from sjtu_login import *


class LoginFrame(tk.Frame):
    def __init__(self, url, callback, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        entry_columnspan = 8

        for i in range(entry_columnspan+1):
            self.columnconfigure(i, weight=1)

        num_row = 0

        self.url = url
        self.callback = callback

        self.username_label = tk.Label(self, text="jAccount用户名")
        self.username_label.grid(column=0, row=num_row)
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self, textvariable=self.username_var)
        self.username_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        num_row += 1

        self.password_label = tk.Label(self, text="jAccount密码")
        self.password_label.grid(column=0, row=num_row)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self,
            show='*',
            textvariable=self.password_var
        )
        self.password_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        num_row += 1

        self.captcha_label = tk.Label(self)
        self.captcha_label.grid(column=0, row=num_row)
        self.captcha_label.bind(
            "<ButtonRelease-1>",
            lambda e: self.refresh_captcha()
        )
        self.captcha_var = tk.StringVar()
        self.captcha_entry = tk.Entry(self, textvariable=self.captcha_var)
        self.captcha_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        num_row += 1

        button_columnspan = 2

        self.refresh_button = tk.Button(
            self, command=self.refresh_all, text="刷新"
        )
        self.refresh_button.grid(
            column=entry_columnspan-button_columnspan+1,
            columnspan=button_columnspan,
            row=num_row,
            sticky=tk.W+tk.E
        )
        self.login_button = tk.Button(
            self, command=self.try_login, text="登录"
        )
        self.login_button.grid(
            column=entry_columnspan-2*button_columnspan+1,
            columnspan=button_columnspan,
            row=num_row,
            sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

        self.refresh_all()

    def refresh_captcha(self):
        self.captcha_img = ImageTk.PhotoImage(
            get_captcha_img(
                self.uuid, self.cookies
            )
        )
        self.captcha_label.configure(
            image=self.captcha_img
        )

    def refresh_all(self):
        self.params, self.uuid, self.cookies = get_params_uuid_cookies(
            self.url
        )
        self.refresh_captcha()

    def try_login(self):
        username = self.username_var.get()
        if not username:
            tkinter.messagebox.showerror("登录失败 (本地)", "请输入用户名")
            return
        password = self.password_var.get()
        if not password:
            tkinter.messagebox.showerror("登录失败 (本地)", "请输入密码")
            return
        captcha = self.captcha_var.get()
        if not captcha:
            tkinter.messagebox.showerror("登录失败 (本地)", "请输入验证码")
            return
        result = login(
            username,
            password,
            self.uuid,
            captcha,
            self.params,
            self.cookies
        )
        if result.url.startswith("https://jaccount.sjtu.edu.cn/jaccount/jalogin"):
            error_message = BeautifulSoup(
                result.content, "html.parser"
            ).find(
                "div", attrs={
                    "id": "div_warn", "class": "warn-info"
                }
            ).text
            tkinter.messagebox.showerror("登录失败 (远程)", error_message)
            self.refresh_all()
        else:
            tkinter.messagebox.showinfo("登录成功", "登录成功")
            self.master.destroy()
            if self.callback is not None:
                self.callback(result.cookies.get_dict())
