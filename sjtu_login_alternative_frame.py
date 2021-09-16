import tkinter as tk
import tkinter.messagebox
from sjtu_login import *


class LoginAlternativeFrame(tk.Frame):
    def __init__(self, callback, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        entry_columnspan = 8

        for i in range(entry_columnspan+1):
            self.columnconfigure(i, weight=1)

        num_row = 0

        self.callback = callback

        self.JSESSIONID_label = tk.Label(self, text="JSESSIONID")
        self.JSESSIONID_label.grid(column=0, row=num_row)
        self.JSESSIONID_var = tk.StringVar()
        self.JSESSIONID_entry = tk.Entry(
            self, textvariable=self.JSESSIONID_var
        )
        self.JSESSIONID_entry.grid(
            column=1, columnspan=entry_columnspan, row=num_row, sticky=tk.W+tk.E
        )
        num_row += 1

        button_columnspan = 2

        self.confirm_button = tk.Button(
            self, command=self.confirm, text="确认"
        )
        self.confirm_button.grid(
            column=entry_columnspan-button_columnspan+1,
            columnspan=button_columnspan,
            row=num_row,
            sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

    def confirm(self):
        JSESSIONID = self.JSESSIONID_var.get()
        if not JSESSIONID:
            tkinter.messagebox.showerror("失败", "请输入JSESSIONID")
            return
        self.master.destroy()
        self.callback({"JSESSIONID": JSESSIONID})
