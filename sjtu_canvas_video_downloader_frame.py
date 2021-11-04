import tkinter as tk
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import re
from sjtu_canvas_video_download import download_courses
from sjtu_canvas_video_helper import create_window


def remove_invalid_chars(s):
    return re.sub(
        r"[<>:\"/\\|?*\s]", "_", s
    )


def get_course_filename_ext(course_link):
    right_index = course_link.find('?')
    left_index = course_link.rfind('.', 0, right_index)
    course_filename_ext = course_link[left_index:right_index]
    return course_filename_ext


class DownloaderFrame(tk.Frame):
    def __init__(self, selected_courses, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        num_row = 0

        entry_columnspan = 8

        button_columnspan = 2

        for i in range(1+entry_columnspan+button_columnspan):
            self.columnconfigure(i, weight=1)

        self.selected_courses = selected_courses

        self.video_dirname_label = tk.Label(
            self,
            text="保存到..."
        )
        self.video_dirname_label.grid(
            row=num_row, column=0
        )
        self.video_dirname_var = tk.StringVar()
        self.video_dirname_entry = tk.Entry(
            self,
            textvariable=self.video_dirname_var
        )
        self.video_dirname_entry.grid(
            row=num_row, column=1, columnspan=entry_columnspan, sticky=tk.W+tk.E
        )
        self.set_video_dirname_button = tk.Button(
            self,
            command=self.set_video_dirname,
            text="浏览"
        )
        self.set_video_dirname_button.grid(
            row=num_row, column=1+entry_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        self.partial_download_checkbutton_var = tk.IntVar()
        self.partial_download_checkbutton = tkinter.ttk.Checkbutton(
            self,
            variable=self.partial_download_checkbutton_var,
            text="只下载录像 (不下载录屏)"
        )
        self.partial_download_checkbutton.grid(
            row=num_row, column=0, columnspan=1+entry_columnspan+button_columnspan
        )
        num_row += 1

        self.preview_button = tk.Button(
            self,
            command=self.preview,
            text="预览"
        )
        self.preview_button.grid(
            row=num_row, column=1+entry_columnspan-button_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        self.initiate_download_button = tk.Button(
            self,
            command=self.initiate_download,
            text="下载"
        )
        self.initiate_download_button.grid(
            row=num_row, column=1+entry_columnspan, columnspan=button_columnspan, sticky=tk.W+tk.E
        )
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

    def get_course_links_filenames(self):
        partial_download = self.partial_download_checkbutton_var.get()
        course_links = []
        course_filenames = []
        for subject in self.selected_courses:
            for course in subject:
                subject_name = remove_invalid_chars(course["subjName"])
                teacher_name = remove_invalid_chars(course["userName"])
                course_name = remove_invalid_chars(course["courName"])
                course_filename_raw = f"{subject_name}_{teacher_name}_{course_name}"
                course_dirname = f"{subject_name}_{teacher_name}"
                if partial_download:
                    for i, video in enumerate(course["videoPlayResponseVoList"]):
                        print(video, type(video['cdviViewNum']))
                        if video['cdviViewNum'] != 0:
                            continue
                        course_link = video["rtmpUrlHdv"]
                        course_filename_ext = get_course_filename_ext(course_link)
                        course_filename = f"{course_dirname}/{course_filename_raw}{course_filename_ext}"
                        course_links.append(course_link)
                        course_filenames.append(course_filename)
                else:
                    for i, video in enumerate(course["videoPlayResponseVoList"]):
                        course_link = video["rtmpUrlHdv"]
                        course_filename_ext = get_course_filename_ext(
                            course_link
                        )
                        course_filename = f"{course_dirname}/{course_filename_raw}_{i}{course_filename_ext}"
                        course_links.append(course_link)
                        course_filenames.append(course_filename)
        return course_links, course_filenames

    def preview(self):
        _, course_filenames = self.get_course_links_filenames()
        window = create_window(self.master)
        tk.Label(window, text='\n'.join(course_filenames)).pack()

    def set_video_dirname(self):
        video_dirname = tkinter.filedialog.askdirectory()
        if video_dirname:
            self.video_dirname_var.set(video_dirname)

    def initiate_download(self):
        video_dirname = self.video_dirname_var.get()
        if not video_dirname:
            tkinter.messagebox.showerror("错误", "请指定保存路径")
            return
        course_links, course_filenames = self.get_course_links_filenames()
        download_courses(course_links, course_filenames, video_dirname)
