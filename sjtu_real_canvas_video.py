import requests
from bs4 import BeautifulSoup


def get_old_external_tool_id(course_id, oc_cookies):
    old_external_tool_id = "9487"
    try:
        elem = (
            BeautifulSoup(
                requests.get(
                    f"https://oc.sjtu.edu.cn/courses/{course_id}",
                    cookies=oc_cookies,
                ).content,
                "html.parser",
            )
            .find("div", attrs={"id": "main"})
            .find(
                "a",
                string=lambda x: x.startswith("课堂视频") and x.endswith("旧版"),
            )
        )

        old_external_tool_id = elem["href"].rpartition("/")[-1]

    except Exception as e:
        print("ERR:", e)
        print(f"using default old_external_tool_id: {old_external_tool_id}")

    return old_external_tool_id


def get_sub_cookies(course_id, oc_cookies):
    old_external_tool_id = get_old_external_tool_id(course_id, oc_cookies)
    data = {
        i["name"]: i["value"]
        for i in
        BeautifulSoup(
            requests.get(
                f"https://oc.sjtu.edu.cn/courses/{course_id}/external_tools/{old_external_tool_id}",
                cookies=oc_cookies
            ).content, "html.parser"
        ).find(
            "form",
            attrs={
                "action": "https://courses.sjtu.edu.cn/lti/launch"
            }
        ).children
        if i.name == "input"
    }

    r = requests.post(
        "https://courses.sjtu.edu.cn/lti/launch",
        data=data,
        allow_redirects=False
    )

    return r.cookies, r.headers["location"].partition("?canvasCourseId=")[-1]


def get_real_canvas_video_single(i, sub_cookies):
    return requests.post(
        "https://courses.sjtu.edu.cn/lti/vodVideo/getVodVideoInfos",
        data={
            "playTypeHls": "true",
            "id": i["videoId"],
            "isAudit": "true"
        },
        cookies=sub_cookies
    ).json()["body"]


class RealCourse:
    def __init__(self, i, sub_cookies):
        self.i = i
        self.sub_cookies = sub_cookies
        self.flag = False
        self.course = None

    def get(self):
        if not self.flag:
            self.flag = True
            self.course = get_real_canvas_video_single(
                self.i, self.sub_cookies
            )
        return self.course

    def __getitem__(self, key):
        return self.get()[key]


def get_real_canvas_videos_using_sub_cookies(sub_cookies, canvasCourseId):
    return [
        [
            RealCourse(i, sub_cookies)
            for i in requests.post(
                "https://courses.sjtu.edu.cn/lti/vodVideo/findVodVideoList",
                data={
                    "pageIndex": "1",
                    "pageSize": "1000",
                    "canvasCourseId": canvasCourseId
                },
                cookies=sub_cookies
            ).json()["body"]["list"]
        ][::-1]
    ]


def get_real_canvas_videos(course_id, oc_cookies):
    sub_cookies, canvasCourseId = get_sub_cookies(course_id, oc_cookies)
    return get_real_canvas_videos_using_sub_cookies(sub_cookies, canvasCourseId)
