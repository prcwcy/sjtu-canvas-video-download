import requests
from bs4 import BeautifulSoup


def get_sub_cookies(course_id, oc_cookies):
    data = {
        i["name"]: i["value"]
        for i in
        BeautifulSoup(
            requests.get(
                f"https://oc.sjtu.edu.cn/courses/{course_id}/external_tools/162",
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


def get_real_canvas_videos_using_sub_cookies(sub_cookies, canvasCourseId):
    return [
        [
            requests.post(
                "https://courses.sjtu.edu.cn/lti/vodVideo/getVodVideoInfos",
                data={
                    "playTypeHls": "true",
                    "id": i["videoId"],
                    "isAudit": "true"
                },
                cookies=sub_cookies
            ).json()["body"]
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
