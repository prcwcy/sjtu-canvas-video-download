import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
from sjtu_canvas_video_download import download_courses
import datetime
from sjtu_history import history, save_history


class HistoryFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        num_row = 0

        combobox_columnspan = 8

        for i in range(combobox_columnspan+1):
            self.columnconfigure(i, weight=1)

        self.task_names = [
            "%d. %s %s等" % (
                i, datetime.datetime.fromtimestamp(
                    task["time"]//1000000000
                ).isoformat(),
                task["course_filenames"][0]
            )
            for i, task in enumerate(history)
        ]

        self.task_label = tk.Label(
            self,
            text="历史"
        )
        self.task_label.grid(
            row=num_row, column=0
        )
        self.task_combobox_var = tk.StringVar()
        self.task_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.task_combobox_var,
            values=self.task_names,
            state="readonly"
        )
        self.task_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        button_columnspan = 1

        self.clear_button = tk.Button(
            self,
            command=self.clear_history,
            text="清空历史记录"
        )
        self.clear_button.grid(
            row=num_row, column=combobox_columnspan+1-2*button_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )

        self.download_button = tk.Button(
            self,
            command=self.initiate_download,
            text="重新下载选中项"
        )
        self.download_button.grid(
            row=num_row, column=combobox_columnspan+1-button_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

    def get_task_index(self):
        task_name = self.task_combobox_var.get()
        if task_name:
            task_index = int(task_name[:task_name.find('.')])
            return task_index
        return -1

    def initiate_download(self):
        task_index = self.get_task_index()
        if task_index == -1:
            tkinter.messagebox.showerror("错误", "请选择一个历史任务")
            return
        task = history[task_index]
        download_courses(
            task["course_links"],
            task["course_filenames"],
            task["video_dirname"],
            True
        )

    def clear_history(self):
        if tkinter.messagebox.askyesno("警告", "是否清空历史记录?"):
            global history
            history.clear()
            self.task_names.clear()
            self.task_combobox_var.set("")
            self.task_combobox.configure(
                values=self.task_names
            )
            save_history()
