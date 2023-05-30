import tkinter as tk
import tkinter.messagebox
from PIL import ImageTk
from sjtu_login import get_params_uuid_cookies
from sjtu_qr_code_login import *


class QRCodeLoginFrame(tk.Frame):
    def __init__(self, url, callback, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        self.url = url
        self.callback = callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.qr_code_label = tk.Label(self)
        self.qr_code_label.grid(
            column=0, row=0,
            sticky=tk.N+tk.S+tk.W+tk.E
        )
        self.qr_code_label.bind(
            "<ButtonRelease-1>",
            lambda e: self.start_refresh_qr_code()
        )

        self.refresh_button = tk.Button(
            self, command=self.refresh_all, text="刷新"
        )
        self.refresh_button.grid(
            column=0, row=1,
            sticky=tk.W+tk.E
        )

        self.wss = None
        self.t = None

        self.bind(
            "<<login>>",
            lambda e: self.login()
        )
        self.refresh_all()

    def start_refresh_qr_code(self):
        send_update_qr_code(self.wss)

    def refresh_qr_code_callback(self, ts, sig):
        self.ts = ts
        self.sig = sig
        self.refresh_qr_code()

    def refresh_qr_code(self):
        self.qr_code_img = ImageTk.PhotoImage(
            get_qr_code_img(
                self.uuid, self.ts, self.sig, self.cookies
            )
        )
        self.qr_code_label.configure(
            image=self.qr_code_img
        )

    def login_callback(self):
        self.event_generate(
            "<<login>>",
            when="tail"
        )

    def login(self):
        tkinter.messagebox.showinfo("登录成功", "登录成功")
        self.master.destroy()
        result = qr_code_login(self.uuid, self.cookies)
        self.callback(result)

    def refresh_all(self):
        self.params, self.uuid, self.cookies, self.url2 = get_params_uuid_cookies(
            self.url
        )
        if self.wss is not None:
            self.wss.close()
            self.t.join()
        self.wss, self.t = get_wss(
            self.uuid, self.cookies,
            self.refresh_qr_code_callback,
            self.login_callback
        )
        self.start_refresh_qr_code()

    def destroy(self):
        if self.wss is not None:
            self.wss.close()
            self.t.join()
        return super().destroy()
