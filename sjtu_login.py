import requests
from PIL import Image
import re
import io
import urllib.parse


def parse_params(url):
    params = dict()
    for s in url[url.find('?')+1:].split('&'):
        i = s.find('=')
        params[urllib.parse.unquote(s[:i])] = urllib.parse.unquote(s[i+1:])
    return params


def get_params_uuid_cookies(url):
    r = requests.get(
        url,
        headers={"accept-language": "zh-CN"}
    )
    params = parse_params(r.url)
    uuid = re.search(
        "(['\"])(uuid)(\\1)(\\s*:\\s*)(['\"])(.*)(\\5)", r.text
    ).group(6)
    cookies = r.cookies.get_dict()
    return params, uuid, cookies


def get_captcha_img(uuid, cookies):
    r = requests.get(
        "https://jaccount.sjtu.edu.cn/jaccount/captcha",
        params={
            "uuid": uuid
        },
        cookies=cookies
    )
    img = Image.open(io.BytesIO(r.content))
    return img


def login(username, password, uuid, captcha, params, cookies):
    r = requests.post(
        "https://jaccount.sjtu.edu.cn/jaccount/ulogin",
        data={
            "user": username,
            "pass": password,
            "uuid": uuid,
            "captcha": captcha,
            **params,
        },
        headers={"accept-language": "zh-CN"},
        cookies=cookies,
    )
    return r
