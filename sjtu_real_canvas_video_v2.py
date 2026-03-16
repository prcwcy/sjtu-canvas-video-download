import base64
import json
from urllib.parse import parse_qsl, quote, urlparse

import requests
from bs4 import BeautifulSoup


def _decode_jwt_payload(token):
    if not token or token.count(".") < 2:
        return {}

    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)

    try:
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}


def _parse_redirect_params(url):
    if not url:
        return {}

    parsed = urlparse(url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    # Some redirects carry parameters after `#/path?...`, so we parse both.
    if "?" in parsed.fragment:
        _, _, fragment_query = parsed.fragment.partition("?")
        params.update(parse_qsl(fragment_query, keep_blank_values=True))

    return params


def _get_canvas_course_id(params_dict, *payload_sources):
    for key in ("courId", "canvasCourseId", "courseId", "ltiCourseId"):
        value = params_dict.get(key)
        if value:
            return str(value)

    for source in payload_sources:
        for key in ("lti_message_hint", "id_token", "state"):
            payload = _decode_jwt_payload(source.get(key))
            value = payload.get("context_id")
            if value:
                return str(value)

            context = payload.get(
                "https://purl.imsglobal.org/spec/lti/claim/context", {}
            )
            if context.get("id"):
                return str(context["id"])

            for fallback_key in ("courId", "canvasCourseId", "courseId", "ltiCourseId"):
                value = payload.get(fallback_key)
                if value:
                    return str(value)

    return None


def _get_nested_value(obj, *path):
    cur = obj
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _extract_video_records(payload):
    if isinstance(payload, list):
        return payload

    candidates = (
        ("data", "records"),
        ("data", "list"),
        ("data", "rows"),
        ("data", "items"),
        ("data", "page", "records"),
        ("data", "page", "list"),
        ("body", "list"),
        ("body",),
        ("data",),
    )

    for path in candidates:
        value = _get_nested_value(payload, *path)
        if isinstance(value, list):
            return value

    return None


def _extract_video_detail(payload):
    for path in (("data",), ("body",)):
        value = _get_nested_value(payload, *path)
        if isinstance(value, dict):
            return value
    return None


def _iter_course_id_candidates(course_id, canvasCourseId):
    candidates = []

    for value in (canvasCourseId, course_id):
        if value is None:
            continue

        value = str(value)
        if value not in candidates:
            candidates.append(value)

        if value.isdigit():
            trimmed = value.lstrip("0")
            if trimmed and trimmed not in candidates:
                candidates.append(trimmed)

        encoded = quote(value, safe="")
        if encoded and encoded not in candidates:
            candidates.append(encoded)

    return candidates


def _request_video_list(sub_cookies, v_header, course_id, canvasCourseId):
    candidate_ids = _iter_course_id_candidates(course_id, canvasCourseId)
    candidate_bodies = []

    for candidate_id in candidate_ids:
        candidate_bodies.extend(
            [
                {"canvasCourseId": candidate_id},
                {"canvasCourseId": candidate_id, "pageIndex": 1, "pageSize": 1000},
                {"courId": candidate_id},
                {"courId": candidate_id, "pageIndex": 1, "pageSize": 1000},
                {"courseId": candidate_id},
                {"ltiCourseId": candidate_id},
            ]
        )

    last_payload = None

    for body in candidate_bodies:
        response = requests.post(
            "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/directOnDemandPlay/findVodVideoList",
            json=body,
            cookies=sub_cookies,
            headers=v_header,
        )
        payload = response.json()
        last_payload = payload
        records = _extract_video_records(payload)
        if records is not None:
            return records

    summary = {}
    if isinstance(last_payload, dict):
        summary = {
            "code": last_payload.get("code"),
            "message": last_payload.get("message") or last_payload.get("msg"),
            "data_type": type(last_payload.get("data")).__name__,
        }

    raise RuntimeError(
        "视频列表接口未返回可识别的数据。"
        f"尝试的课程ID: {candidate_ids}，最后一次返回: {summary}"
    )


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
    launch_form = BeautifulSoup(
        requests.get(
            f"https://oc.sjtu.edu.cn/courses/{course_id}/external_tools/{external_tool_id}",
            cookies=oc_cookies,
        ).content,
        "html.parser",
    ).find(
        "form",
        attrs={
            "action": "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/oidc/login_initiations"
        }
    )

    if launch_form is None:
        raise RuntimeError("未找到视频平台登录表单，可能是 Cookie 已失效，或课程页面结构已变化。")

    data = {
        i["name"]: i["value"]
        for i in launch_form.children
        if i.name == "input"
    }

    r = requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/oidc/login_initiations",
        data=data,
        cookies=oc_cookies,
        allow_redirects=True
    )

    auth_form = BeautifulSoup(
        r.content, "html.parser"
    ).find(
        "form",
        attrs={
            "action": "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/lti3Auth/ivs"
        }
    )

    if auth_form is None:
        raise RuntimeError("未找到 LTI 鉴权表单，可能是登录状态失效，或学校视频平台返回流程已变化。")

    data_2 = {
        i["name"]: i["value"]
        for i in auth_form.children
        if i.name == "input"
    }

    r_2 = requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/lti3Auth/ivs",
        data=data_2,
        cookies=oc_cookies,
        allow_redirects=False
    )

    loc = r_2.headers.get("location")
    params_dict = _parse_redirect_params(loc)

    tokenId = params_dict.get("tokenId")
    canvasCourseId = _get_canvas_course_id(params_dict, data, data_2)

    if not tokenId:
        raise RuntimeError(
            f"未能从视频平台跳转中解析 tokenId，当前返回字段: {sorted(params_dict.keys())}"
        )

    if not canvasCourseId:
        raise RuntimeError(
            "未能从视频平台跳转或 LTI 参数中解析课程ID，"
            f"当前返回字段: {sorted(params_dict.keys())}"
        )

    r_3 = requests.get(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/lti3/getAccessTokenByTokenId",
        params={"tokenId": tokenId, },
        cookies=oc_cookies,
    )

    token_payload = r_3.json()["data"]
    access_token = token_payload["token"]
    access_params = token_payload.get("params") or {}

    # The video platform uses params.courId as the canonical course id for
    # directOnDemandPlay APIs. Falling back to earlier parsed ids is less reliable.
    canvasCourseId = (
        access_params.get("courId")
        or access_params.get("canvasCourseId")
        or access_params.get("courseId")
        or access_params.get("ltiCourseId")
        or canvasCourseId
    )

    v_header = {
        "token": access_token
    }

    return oc_cookies, canvasCourseId, v_header


def get_real_canvas_video_single_v2(i, sub_cookies, v_header):
    payload = requests.post(
        "https://v.sjtu.edu.cn/jy-application-canvas-sjtu/directOnDemandPlay/getVodVideoInfos",
        data={
            "playTypeHls": "true",
            "id": i["videoId"],
            "isAudit": "true"
        },
        cookies=sub_cookies,
        headers=v_header,
    ).json()

    detail = _extract_video_detail(payload)
    if detail is None:
        raise RuntimeError(
            "视频详情接口未返回可识别的数据。"
            f" 返回字段: {sorted(payload.keys()) if isinstance(payload, dict) else type(payload).__name__}"
        )

    return detail


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


def get_real_canvas_videos_using_sub_cookies_v2(sub_cookies, course_id, canvasCourseId, v_header):
    records = _request_video_list(sub_cookies, v_header, course_id, canvasCourseId)

    return [
        [
            RealCourseV2(i, sub_cookies, v_header)
            for i in records
        ]
    ]


def get_real_canvas_videos_v2(course_id, oc_cookies):
    sub_cookies, canvasCourseId, v_header = get_sub_cookies_v2(
        course_id, oc_cookies)
    return get_real_canvas_videos_using_sub_cookies_v2(
        sub_cookies, course_id, canvasCourseId, v_header
    )
