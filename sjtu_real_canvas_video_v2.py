import requests
from bs4 import BeautifulSoup



def get_external_tool_id(course_id, oc_cookies):
    external_tool_id = "8329"
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
                string=lambda x: x.startswith("课堂视频") and not x.endswith("旧版"),
            )
        )

        external_tool_id = elem["href"].rpartition("/")[-1]

    except Exception as e:
        print("ERR:", e)
        print(f"using default external_tool_id: {external_tool_id}")

    return external_tool_id


def get_sub_cookies_v2(course_id, oc_cookies):
    external_tool_id = get_external_tool_id(course_id, oc_cookies)
    data = {
        i["name"]: i["value"]
        for i in
        BeautifulSoup(
            requests.get(
                f"https://oc.sjtu.edu.cn/courses/{course_id}/external_tools/{external_tool_id}",
                cookies=oc_cookies,
            ).content, "html.parser"
        ).find(
            "form",
            attrs={
                "action": "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/oidc/login_initiations"
            }
        ).children
        if i.name == "input"
    }

    r = requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/oidc/login_initiations",
        data=data,
        cookies=oc_cookies,
        allow_redirects=True
    )

    data_2 = {
        i["name"]: i["value"]
        for i in
        BeautifulSoup(
            r.content, "html.parser"
        ).find(
            "form",
            attrs={
                "action": "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/lti3Auth/ivs"
            }
        ).children
        if i.name == "input"
    }

    r_2 = requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/lti3Auth/ivs",
        data=data_2,
        cookies=oc_cookies,
        allow_redirects=False
    )

    loc = r_2.headers.get("location")

    params_arr = [i.partition('=') for i in loc.partition('?')[-1].split('&')]

    params_dict = {i: j for i, _, j in params_arr}

    tokenId = params_dict["tokenId"]
    canvasCourseId = params_dict["courId"]

    r_3 = requests.get(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/getAccessTokenByTokenId",
        params={"tokenId": tokenId, },
        cookies=oc_cookies,
    )

    access_token = r_3.json()["data"]["token"]

    v_header = {
        "token": access_token
    }

    return oc_cookies, canvasCourseId, v_header


def get_real_canvas_video_single_v2(i, sub_cookies, v_header):
    return requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/directOnDemandPlay/getVodVideoInfos",
        data={
            "playTypeHls": "true",
            "id": i["videoId"],
            "isAudit": "true"
        },
        cookies=sub_cookies,
        headers=v_header,
    ).json()["data"]


class RealCourseV2:
    def __init__(self, i, sub_cookies, v_header):
        self.i = i
        self.sub_cookies = sub_cookies
        self.v_header = v_header
        self.flag = False
        self.course = None

    def get(self):
        if not self.flag:
            self.flag = True
            self.course = get_real_canvas_video_single_v2(
                self.i, self.sub_cookies, self.v_header
            )
        return self.course

    def __getitem__(self, key):
        return self.get()[key]


def get_real_canvas_videos_using_sub_cookies_v2(sub_cookies, canvasCourseId, v_header):
    return [
        [
            RealCourseV2(i, sub_cookies, v_header)
            for i in requests.post(
                "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/directOnDemandPlay/findVodVideoList",
                json={
                    "canvasCourseId": canvasCourseId
                },
                cookies=sub_cookies,
                headers=v_header,
            ).json()["data"]["records"]
        ]
    ]


def get_real_canvas_videos_v2(course_id, oc_cookies):
    sub_cookies, canvasCourseId, v_header = get_sub_cookies_v2(
        course_id, oc_cookies)
    return get_real_canvas_videos_using_sub_cookies_v2(sub_cookies, canvasCourseId, v_header)
