import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from sjtu_login_frame import LoginFrame
from sjtu_login_alternative_frame import LoginAlternativeFrame
from sjtu_qr_code_login_frame import QRCodeLoginFrame
from sjtu_canvas_video_picker_frame import SinglePickerFrame, MultiplePickerFrame
from sjtu_canvas_video_helper import create_window
from sjtu_canvas_video import get_all_courses
from sjtu_real_canvas_video import get_real_canvas_videos, get_real_canvas_videos_using_sub_cookies
import json


class MainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.urls = [
            "https://courses.sjtu.edu.cn/app/oauth/2.0/login?login_type=outer",
            "https://oc.sjtu.edu.cn/login/openid_connect"
        ]
        self.url_idx = 0

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
        self.login_button.grid(column=0, row=num_row)
        self.qr_code_login_button = tk.Button(
            self,
            command=self.popup_qr_code_login,
            text="登录jAccount (二维码)"
        )
        self.qr_code_login_button.grid(column=1, row=num_row)
        self.login_alternative_button = tk.Button(
            self,
            command=self.popup_login_alternative,
            text="输入JSESSIONID (开发者入口)"
        )
        self.login_alternative_button.grid(column=2, row=num_row, columnspan=2)
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
            column=1, row=num_row, columnspan=2, sticky=tk.W+tk.E
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

    def course_id_checkbutton_changed(self):
        if self.course_id_checkbutton_var.get():
            self.url_idx = 1
            self.course_id_entry.config(state=tk.NORMAL)
        else:
            self.url_idx = 0
            self.course_id_entry.config(state=tk.DISABLED)

    def refresh_status_label(self):
        num_subject = len(self.all_courses)
        num_course = sum([len(courses) for courses in self.all_courses])
        self.status_label.configure(
            text=f"当前已读取到: {num_subject}个科目, 共{num_course}讲"
        )

    def refresh_all_courses(self, cookies):
        if self.course_id_checkbutton_var.get():
            if type(cookies) == dict:
                self.all_courses = get_real_canvas_videos_using_sub_cookies(
                    cookies
                )
            else:
                course_id = self.course_id_var.get()
                if not course_id:
                    tkinter.messagebox.showerror("错误", "请输入课程ID")
                    return
                self.all_courses = get_real_canvas_videos(course_id, cookies)
        else:
            self.all_courses = get_all_courses(cookies)
        self.refresh_status_label()

    def popup_login(self):
        if self.course_id_checkbutton_var.get() and not self.course_id_var.get():
            tkinter.messagebox.showerror("错误", "请输入课程ID")
            return
        window = create_window(self.master)
        window.geometry("400x200")
        LoginFrame(
            self.urls[self.url_idx],
            lambda cookies: self.refresh_all_courses(cookies),
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

    def popup_login_alternative(self):
        window = create_window(self.master)
        window.geometry("400x100")
        LoginAlternativeFrame(
            lambda cookies: self.refresh_all_courses(cookies),
            window
        )

    def popup_qr_code_login(self):
        if self.course_id_checkbutton_var.get() and not self.course_id_var.get():
            tkinter.messagebox.showerror("错误", "请输入课程ID")
            return
        window = create_window(self.master)
        window.geometry("300x300")
        QRCodeLoginFrame(
            self.urls[self.url_idx],
            lambda cookies: self.refresh_all_courses(cookies),
            window
        )
