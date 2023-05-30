import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
import sys
import os
import json
from PIL import ImageTk
from sjtu_login import *

self_dirname = os.path.dirname(sys.argv[0])
config_filename = os.path.join(self_dirname, "config.json")


class LoginFrame(tk.Frame):
    def __init__(self, url, callback, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        entry_columnspan = 8

        for i in range(1+entry_columnspan+1):
            self.columnconfigure(i, weight=1)

        num_row = 0

        if os.path.isfile(config_filename):
            with open(config_filename, encoding="utf-8") as config_file:
                config = json.load(config_file)
            self.config_username = config["username"]
            self.config_password = config["password"]
        else:
            self.config_username = ""
            self.config_password = ""

        self.url = url
        self.callback = callback

        self.username_label = tk.Label(self, text="jAccount用户名")
        self.username_label.grid(column=0, row=num_row)
        self.username_var = tk.StringVar(
            value=self.config_username
        )
        self.username_entry = tk.Entry(self, textvariable=self.username_var)
        self.username_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        self.username_checkbutton_var = tk.IntVar(
            value=True
        )
        self.username_checkbutton = tkinter.ttk.Checkbutton(
            self,
            command=self.username_checkbutton_changed,
            variable=self.username_checkbutton_var,
            text="记住"
        )
        self.username_checkbutton.grid(
            column=1+entry_columnspan, row=num_row
        )
        num_row += 1

        self.password_label = tk.Label(self, text="jAccount密码")
        self.password_label.grid(column=0, row=num_row)
        self.password_var = tk.StringVar(
            value=self.config_password
        )
        self.password_entry = tk.Entry(
            self,
            show='*',
            textvariable=self.password_var
        )
        self.password_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        self.password_checkbutton_var = tk.IntVar(
            value=int(bool(self.config_password))
        )
        self.password_checkbutton = tkinter.ttk.Checkbutton(
            self,
            command=self.password_checkbutton_changed,
            variable=self.password_checkbutton_var,
            text="记住"
        )
        self.password_checkbutton.grid(
            column=1+entry_columnspan, row=num_row
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
                self.uuid, self.cookies, self.url2
            )
        )
        self.captcha_label.configure(
            image=self.captcha_img
        )

    def refresh_all(self):
        self.params, self.uuid, self.cookies, self.url2 = get_params_uuid_cookies(
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
        if result is None:
            tkinter.messagebox.showerror("登录失败 (远程)", "请正确填写用户名, 密码和验证码")
            self.refresh_all()
        else:
            tkinter.messagebox.showinfo("登录成功", "登录成功")
            self.master.destroy()
            if not self.username_checkbutton_var.get():
                username = ""
            if not self.password_checkbutton_var.get():
                password = ""
            if self.config_username != username or self.config_password != password:
                config = {
                    "username": username,
                    "password": password
                }
                with open(config_filename, "w", encoding="utf-8") as config_file:
                    json.dump(
                        config,
                        config_file,
                        ensure_ascii=False,
                        check_circular=False
                    )
            self.callback(result)

    def username_checkbutton_changed(self):
        if not self.username_checkbutton_var.get():
            self.password_checkbutton_var.set(False)

    def password_checkbutton_changed(self):
        if self.password_checkbutton_var.get():
            self.username_checkbutton_var.set(True)
