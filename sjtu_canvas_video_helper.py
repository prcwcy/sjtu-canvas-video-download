import tkinter as tk


def create_window(master):
    window = tk.Toplevel(master)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    return window
