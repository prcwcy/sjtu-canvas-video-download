import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from sjtu_login import login_using_cookies
from sjtu_login_frame import LoginFrame
from sjtu_qr_code_login_frame import QRCodeLoginFrame
from sjtu_canvas_video_picker_frame import SinglePickerFrame, MultiplePickerFrame
from sjtu_canvas_video_helper import create_window
from sjtu_canvas_video import get_all_courses
from sjtu_real_canvas_video_v2 import get_real_canvas_videos_v2 as get_real_canvas_videos
# from sjtu_real_canvas_video import get_real_canvas_videos as get_real_canvas_videos
from sjtu_history_frame import HistoryFrame
import json


class MainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.urls = [
            "https://courses.sjtu.edu.cn/app/oauth/2.0/login?login_type=outer",
            "https://oc.sjtu.edu.cn/login/openid_connect"
        ]

        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        num_row = 0

        self.login_label = tk.Label(
            self,
            text="第一次使用本工具, 请点击下方的按钮登录jAccount, 以获取Canvas视频信息."
        )
        self.login_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1
        self.login_button = tk.Button(
            self,
            command=self.popup_login,
            text="登录jAccount"
        )
        self.login_button.grid(column=1, row=num_row)
        self.qr_code_login_button = tk.Button(
            self,
            command=self.popup_qr_code_login,
            text="登录jAccount (二维码)"
        )
        self.qr_code_login_button.grid(column=2, row=num_row)
        num_row += 1

        self.import_label = tk.Label(
            self,
            text="如果此前已经使用本工具获取并保存了Canvas视频信息, 请点击下方的按钮导入该文件."
        )
        self.import_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1
        self.import_button = tk.Button(
            self,
            command=self.popup_import,
            text="导入下载地址"
        )
        self.import_button.grid(column=0, row=num_row, columnspan=4)
        num_row += 1

        self.export_label = tk.Label(
            self,
            text="建议在获取Canvas视频信息后, 点击下方的按钮将其保存为文件."
        )
        self.export_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1
        self.export_button = tk.Button(
            self,
            command=self.popup_export,
            text="保存下载地址"
        )
        self.export_button.grid(column=0, row=num_row, columnspan=4)
        num_row += 1

        self.history_label = tk.Label(
            self,
            text="点击下方的按钮继续之前未完成的下载."
        )
        self.history_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1
        self.history_button = tk.Button(
            self,
            command=self.popup_history,
            text="历史"
        )
        self.history_button.grid(column=0, row=num_row, columnspan=4)
        num_row += 1

        self.download_label = tk.Label(
            self,
            text="获取Canvas视频信息后, 可点击下方的按钮下载视频."
        )
        self.download_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1
        self.download_single_button = tk.Button(
            self,
            command=self.popup_download_single,
            text="单个下载"
        )
        self.download_single_button.grid(column=0, row=num_row, columnspan=2)
        self.download_multiple_button = tk.Button(
            self,
            command=self.popup_download_multiple,
            text="批量下载"
        )
        self.download_multiple_button.grid(column=2, row=num_row, columnspan=2)
        num_row += 1

        self.course_id_label = tk.Label(self, text="课程ID")
        self.course_id_label.grid(column=0, row=num_row)
        self.course_id_var = tk.StringVar()
        self.course_id_entry = tk.Entry(
            self,
            textvariable=self.course_id_var,
            state=tk.DISABLED
        )
        self.course_id_entry.grid(
            column=1, row=num_row
        )
        self.course_id_checkbutton_var = tk.IntVar(
            value=False
        )
        self.course_id_checkbutton = tkinter.ttk.Checkbutton(
            self,
            variable=self.course_id_checkbutton_var,
            command=self.course_id_checkbutton_changed,
            text="使用课程ID"
        )
        self.course_id_checkbutton.grid(
            column=2, row=num_row
        )
        self.course_id_update_button = tk.Button(
            self,
            command=self.update_course_id,
            text="更新课程ID"
        )
        self.course_id_update_button.grid(
            column=3, row=num_row
        )
        num_row += 1

        self.status_label = tk.Label(self)
        self.status_label.grid(column=0, row=num_row, columnspan=4)
        num_row += 1

        for i in range(num_row):
            self.rowconfigure(i, weight=1)

        self.all_courses = []
        self.refresh_status_label()

        self.cookies = None

    def course_id_checkbutton_changed(self):
        if self.course_id_checkbutton_var.get():
            self.course_id_entry.config(state=tk.NORMAL)
        else:
            self.course_id_entry.config(state=tk.DISABLED)

    def refresh_status_label(self):
        num_subject = len(self.all_courses)
        num_course = sum([len(courses) for courses in self.all_courses])
        self.status_label.configure(
            text=f"当前已读取到: {num_subject}个科目, 共{num_course}讲"
        )

    def update_cookies_and_refresh_all_courses(self, cookies):
        login_using_cookies(self.urls[1], cookies)
        self.cookies = cookies
        self.refresh_all_courses()

    def refresh_all_courses(self):
        if self.course_id_checkbutton_var.get():
            course_id = self.course_id_var.get()
            if not course_id:
                tkinter.messagebox.showerror("错误", "请输入课程ID")
                return
            self.all_courses = get_real_canvas_videos(course_id, self.cookies)
        else:
            self.all_courses = get_all_courses(self.cookies)
        self.refresh_status_label()

    def popup_login(self):
        window = create_window(self.master)
        window.geometry("400x200")
        LoginFrame(
            self.urls[0],
            lambda cookies: self.update_cookies_and_refresh_all_courses(
                cookies
            ),
            window
        )

    def popup_import(self):
        filename = tkinter.filedialog.askopenfilename(
            filetypes=(
                ("", "*.json"),
            )
        )
        if filename:
            with open(filename, encoding="utf-8") as f:
                self.all_courses = json.load(f)
            self.refresh_status_label()

    def popup_export(self):
        filename = tkinter.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(
                ("", "*.json"),
            )
        )
        for i, subject in enumerate(self.all_courses):
            for j, course in enumerate(subject):
                if type(course) is not dict:
                    self.all_courses[i][j] = course.get()
        if filename:
            with open(filename, mode="w", encoding="utf-8") as f:
                json.dump(
                    self.all_courses, f,
                    ensure_ascii=False,
                    check_circular=False,
                    indent=4
                )

    def popup_download_single(self):
        window = create_window(self.master)
        window.geometry("400x160")
        SinglePickerFrame(self.all_courses, window)

    def popup_download_multiple(self):
        window = create_window(self.master)
        window.geometry("400x200")
        MultiplePickerFrame(self.all_courses, window)

    def popup_qr_code_login(self):
        window = create_window(self.master)
        window.geometry("300x300")
        QRCodeLoginFrame(
            self.urls[0],
            lambda cookies: self.update_cookies_and_refresh_all_courses(
                cookies
            ),
            window
        )

    def update_course_id(self):
        if self.cookies == None:
            tkinter.messagebox.showerror("错误", "请登录")
        else:
            self.refresh_all_courses()

    def popup_history(self):
        window = create_window(self.master)
        window.geometry("400x160")
        HistoryFrame(window)
