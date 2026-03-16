import time
import os
import sys
import subprocess
import shutil
import tkinter.messagebox

import requests
from sjtu_history import history, save_history

self_dirname = os.path.dirname(sys.argv[0])

tmp_dirname = os.path.join(self_dirname, "tmp")
os.makedirs(tmp_dirname, exist_ok=True)

aria2_exe_filename = os.path.join(
    self_dirname, "aria2", "aria2c.exe"
)


def get_aria2_command():
    if sys.platform == "win32" and os.path.isfile(aria2_exe_filename):
        return aria2_exe_filename

    return shutil.which("aria2c")


def download_courses_with_builtin_downloader(course_links, course_filenames, video_dirname):
    headers = {
        "Referer": "https://courses.sjtu.edu.cn"
    }

    for course_link, course_filename in zip(course_links, course_filenames):
        output_filename = os.path.join(video_dirname, course_filename)
        output_dirname = os.path.dirname(output_filename)
        if output_dirname:
            os.makedirs(output_dirname, exist_ok=True)

        tmp_output_filename = output_filename + ".part"
        with requests.get(
            course_link,
            headers=headers,
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            with open(tmp_output_filename, mode="wb") as output_file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output_file.write(chunk)

        os.replace(tmp_output_filename, output_filename)


def download_courses(course_links, course_filenames, video_dirname, no_record=False):
    if not no_record:
        history.append(
            {
                "time": time.time_ns(),
                "course_links": course_links,
                "course_filenames": course_filenames,
                "video_dirname": video_dirname
            }
        )
        save_history()
    aria2_txt_filename = os.path.join(tmp_dirname, f"{time.time_ns()}.txt")
    with open(aria2_txt_filename, mode="w", encoding="utf-8") as aria2_txt_file:
        for course_link, course_filename in zip(course_links, course_filenames):
            print(course_link, file=aria2_txt_file)
            print(
                f" out={course_filename}", file=aria2_txt_file
            )
            print(
                " header=referer: https://courses.sjtu.edu.cn",
                file=aria2_txt_file
            )
    aria2_command = get_aria2_command()
    if sys.platform == "win32":
        if aria2_command:
            subprocess.Popen(
                [
                    aria2_command,
                    "-d", video_dirname,
                    "-i", aria2_txt_filename,
                    "-x", str(16),
                    "--auto-file-renaming=false"
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            tkinter.messagebox.showinfo(
                "提示",
                "未检测到 aria2c，改用内置下载器，速度可能较慢。"
            )
            download_courses_with_builtin_downloader(
                course_links, course_filenames, video_dirname
            )
    else:
        if aria2_command:
            tkinter.messagebox.showinfo("提示", "请查看控制台输出")
            try:
                subprocess.run(
                    [
                        aria2_command,
                        "-d", video_dirname,
                        "-i", aria2_txt_filename,
                        "-x", str(16),
                        "--auto-file-renaming=false"
                    ]
                )
            except KeyboardInterrupt:
                pass
        else:
            tkinter.messagebox.showinfo(
                "提示",
                "未检测到 aria2c，改用内置下载器，速度可能较慢。"
            )
            download_courses_with_builtin_downloader(
                course_links, course_filenames, video_dirname
            )
