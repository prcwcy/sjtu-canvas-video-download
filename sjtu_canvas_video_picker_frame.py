import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
from sjtu_canvas_video_downloader_frame import DownloaderFrame
from sjtu_canvas_video_helper import create_window


class SinglePickerFrame(tk.Frame):
    def __init__(self, all_courses, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        num_row = 0

        combobox_columnspan = 8

        for i in range(combobox_columnspan+1):
            self.columnconfigure(i, weight=1)

        self.all_courses = all_courses

        self.subject_names = [
            "%d. %s" % (i, subject[0]["subjName"])
            for i, subject in enumerate(all_courses)
        ]

        self.course_names = [
            [
                "%d. %s" % (i, course["courName"])
                for i, course in enumerate(subject)
            ]
            for subject in all_courses
        ]

        self.subject_label = tk.Label(
            self,
            text="科目"
        )
        self.subject_label.grid(
            row=num_row, column=0
        )
        self.subject_combobox_var = tk.StringVar()
        self.subject_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.subject_combobox_var,
            values=self.subject_names,
            state="readonly"
        )
        self.subject_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self.update_course_combobox()
        )
        self.subject_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        self.course_label = tk.Label(
            self,
            text="讲"
        )
        self.course_label.grid(
            row=num_row, column=0
        )
        self.course_combobox_var = tk.StringVar()
        self.course_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.course_combobox_var,
            state="readonly"
        )
        self.course_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        button_columnspan = 2

        self.download_button = tk.Button(
            self,
            command=self.initiate_download,
            text="下载"
        )
        self.download_button.grid(
            row=num_row, column=combobox_columnspan+1-button_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

    def get_subject_index(self):
        subject_name = self.subject_combobox_var.get()
        if subject_name:
            subject_index = int(subject_name[:subject_name.find('.')])
            return subject_index
        return -1

    def get_course_index(self):
        course_name = self.course_combobox_var.get()
        if course_name:
            course_index = int(course_name[:course_name.find('.')])
            return course_index
        return -1

    def update_course_combobox(self):
        subject_index = self.get_subject_index()
        self.course_combobox.configure(
            values=self.course_names[subject_index]
        )
        self.course_combobox.current(
            len(
                self.course_names[subject_index]
            )-1
        )

    def initiate_download(self):
        subject_index = self.get_subject_index()
        if subject_index == -1:
            tkinter.messagebox.showerror("错误", "请选择科目")
            return
        course_index = self.get_course_index()
        selected_courses = [[self.all_courses[subject_index][course_index]]]
        window = create_window(self.master)
        window.geometry("400x200")
        DownloaderFrame(selected_courses, window)


class MultiplePickerFrame(tk.Frame):
    def __init__(self, all_courses, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        num_row = 0

        combobox_columnspan = 8

        for i in range(combobox_columnspan+1):
            self.columnconfigure(i, weight=1)

        self.all_courses = all_courses

        self.subject_names = [
            "%d. %s" % (i, subject[0]["subjName"])
            for i, subject in enumerate(all_courses)
        ]

        self.course_names = [
            [
                "%d. %s" % (i, course["courName"])
                for i, course in enumerate(subject)
            ]
            for subject in all_courses
        ]

        self.subject_label = tk.Label(
            self,
            text="科目"
        )
        self.subject_label.grid(
            row=num_row, column=0
        )
        self.subject_combobox_var = tk.StringVar()
        self.subject_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.subject_combobox_var,
            values=self.subject_names,
            state="readonly"
        )
        self.subject_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self.update_course_combobox()
        )
        self.subject_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        self.lower_course_label = tk.Label(
            self,
            text="讲 (起始)"
        )
        self.lower_course_label.grid(
            row=num_row, column=0
        )
        self.lower_course_combobox_var = tk.StringVar()
        self.lower_course_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.lower_course_combobox_var,
            state="readonly"
        )
        self.lower_course_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        self.upper_course_label = tk.Label(
            self,
            text="讲 (终止)"
        )
        self.upper_course_label.grid(
            row=num_row, column=0
        )
        self.upper_course_combobox_var = tk.StringVar()
        self.upper_course_combobox = tkinter.ttk.Combobox(
            self,
            textvariable=self.upper_course_combobox_var,
            state="readonly"
        )
        self.upper_course_combobox.grid(
            row=num_row, column=1, columnspan=combobox_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        button_columnspan = 2

        self.download_button = tk.Button(
            self,
            command=self.initiate_download,
            text="下载"
        )
        self.download_button.grid(
            row=num_row, column=combobox_columnspan+1-button_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

    def get_subject_index(self):
        subject_name = self.subject_combobox_var.get()
        if subject_name:
            subject_index = int(subject_name[:subject_name.find('.')])
            return subject_index
        return -1

    def get_lower_course_index(self):
        lower_course_name = self.lower_course_combobox_var.get()
        if lower_course_name:
            lower_course_index = int(
                lower_course_name[:lower_course_name.find('.')]
            )
            return lower_course_index
        return -1

    def get_upper_course_index(self):
        upper_course_name = self.upper_course_combobox_var.get()
        if upper_course_name:
            upper_course_index = int(
                upper_course_name[:upper_course_name.find('.')]
            )
            return upper_course_index
        return -1

    def update_course_combobox(self):
        subject_index = self.get_subject_index()
        self.lower_course_combobox.configure(
            values=self.course_names[subject_index]
        )
        self.upper_course_combobox.configure(
            values=self.course_names[subject_index]
        )
        self.lower_course_combobox.current(0)
        self.upper_course_combobox.current(
            len(
                self.course_names[subject_index]
            )-1
        )

    def initiate_download(self):
        subject_index = self.get_subject_index()
        if subject_index == -1:
            tkinter.messagebox.showerror("错误", "请选择科目")
            return
        lower_course_index = self.get_lower_course_index()
        upper_course_index = self.get_upper_course_index()
        if upper_course_index < lower_course_index:
            lower_course_index, upper_course_index = upper_course_index, lower_course_index
        selected_courses = [
            self.all_courses[subject_index]
                            [lower_course_index:upper_course_index+1]
        ]
        window = create_window(self.master)
        window.geometry("400x200")
        DownloaderFrame(selected_courses, window)
