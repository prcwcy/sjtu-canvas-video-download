import time
import os
import sys
import subprocess

self_dirname = os.path.dirname(sys.argv[0])

tmp_dirname = os.path.join(self_dirname, "tmp")
os.makedirs(tmp_dirname, exist_ok=True)

aria2_exe_filename = os.path.join(
    self_dirname, "aria2", "aria2c.exe"
)


def download_courses(course_links, course_filenames, video_dirname):
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
    subprocess.run(
        [
            aria2_exe_filename,
            "-d", video_dirname,
            "-i", aria2_txt_filename,
            "-x", "16"
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
