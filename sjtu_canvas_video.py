import requests
from bs4 import BeautifulSoup
from hashlib import md5
import base64
import time
import random


oauth_href = "https://courses.sjtu.edu.cn/app/vodvideo/vodVideoPlay.d2j"
oauth_path = base64.b64encode(oauth_href.encode("utf-8")).decode("utf-8")


def get_oauth_consumer_key(cookies):
    try:
        oauth_consumer_key = base64.b64decode(
            BeautifulSoup(
                requests.get(
                    "https://courses.sjtu.edu.cn/app/vodvideo/vodVideoPlay.d2j?ssoCheckToken=ssoCheckToken&refreshToken=&accessToken=&userId=&",
                    cookies=cookies
                ).content, "html.parser"
            ).find(
                "meta",
                id="xForSecName"
            )["vaule"]
        ).decode("utf-8")
        return oauth_consumer_key
    except Exception:
        pass
    return None


def get_random_uuid(length):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    last_idx = len(chars)-1
    uuid = []
    for i in range(length):
        uuid.append(chars[random.randint(0, last_idx)])
    return ''.join(uuid)


# oauth_randomP1 = f"oauth_{get_random_uuid(5)}"
# oauth_randomP1_val = get_random_uuid(8)
# oauth_randomP2 = f"oauth_{get_random_uuid(5)}"
# oauth_randomP2_val = get_random_uuid(8)
oauth_randomP1 = "oauth_ABCDE"
oauth_randomP1_val = "ABCDEFGH"
oauth_randomP2 = "oauth_VWXYZ"
oauth_randomP2_val = "STUVWXYZ"
oauth_random = f"{oauth_randomP1}={oauth_randomP1_val}&{oauth_randomP2}={oauth_randomP2_val}"


def get_oauth_signature(course_id, oauth_nonce, oauth_consumer_key):
    return md5((f"/app/system/resource/vodVideo/getvideoinfos?id={course_id}&oauth-consumer-key={oauth_consumer_key}&oauth-nonce={oauth_nonce}&oauth-path={oauth_path}&{oauth_random}&playTypeHls=true").encode("utf-8")).hexdigest()


def get_subject_ids(cookies):
    subject_ids = []
    tecl_ids = []
    try:
        subject_list = requests.get(
            "https://courses.sjtu.edu.cn/app/system/course/subject/findSubjectVodList",
            params={
                "pageIndex": 1,
                "pageSize": 128
            },
            headers={
                "accept": "application/json"
            },
            cookies=cookies
        ).json()
        for subj in subject_list["list"]:
            try:
                subject_id = subj["subjectId"]
                tecl_id = subj["teclId"]
            except Exception:
                continue
            subject_ids.append(subject_id)
            tecl_ids.append(tecl_id)
    except Exception:
        pass
    return subject_ids, tecl_ids


def get_course_ids(subject_id, tecl_id, cookies):
    try:
        courses = requests.get(
            "https://courses.sjtu.edu.cn/app/system/resource/vodVideo/getCourseListBySubject",
            params={
                "orderField": "courTimes",
                "subjectId": subject_id,
                "teclId": tecl_id
            },
            headers={"accept": "application/json"},
            cookies=cookies
        ).json()["list"][0]
        course_ids = [
            course["id"]
            for course in courses["responseVoList"]
        ]
        return course_ids
    except Exception:
        pass
    return None


def get_course(course_id, cookies, oauth_consumer_key):
    oauth_nonce = time.time_ns()//1000000
    oauth_signature = get_oauth_signature(
        course_id, oauth_nonce, oauth_consumer_key
    )
    try:
        course = requests.post(
            "https://courses.sjtu.edu.cn/app/system/resource/vodVideo/getvideoinfos",
            data={
                "playTypeHls": "true",
                "id": course_id,
                oauth_randomP1: oauth_randomP1_val,
                oauth_randomP2: oauth_randomP2_val
            },
            headers={
                "accept": "application/json",
                "oauth-consumer-key": oauth_consumer_key,
                "oauth-nonce": str(oauth_nonce),
                "oauth-path": oauth_path,
                "oauth-signature": oauth_signature
            },
            cookies=cookies
        ).json()
        return course
    except Exception:
        pass
    return None


def get_all_courses(cookies):
    all_courses = []
    oauth_consumer_key = get_oauth_consumer_key(cookies)
    if oauth_consumer_key is None:
        return all_courses
    subject_ids, tecl_ids = get_subject_ids(cookies)
    for subject_id, tecl_id in zip(subject_ids, tecl_ids):
        course_ids = get_course_ids(subject_id, tecl_id, cookies)
        if course_ids is None:
            continue
        courses = []
        for course_id in course_ids:
            course = get_course(course_id, cookies, oauth_consumer_key)
            if course is None:
                continue
            if "loginUserId" in course:
                del course["loginUserId"]
            courses.append(course)
        if courses:
            all_courses.append(courses)
    return all_courses
