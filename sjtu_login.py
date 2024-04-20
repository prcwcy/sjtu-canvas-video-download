import requests
from PIL import Image
from bs4 import BeautifulSoup
import io
import urllib.parse
import time


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
    uuid = BeautifulSoup(r.content, 'html.parser').find('a', attrs={'id': 'firefox_link'})['href'].split('=')[1]
    cookies = r.cookies
    for i in r.history:
        cookies.update(i.cookies)
    return params, uuid, cookies, r.url


def get_captcha_img(uuid, cookies, url2):
    r = requests.get(
        "https://jaccount.sjtu.edu.cn/jaccount/captcha",
        params={
            "uuid": uuid,
            "t": time.time_ns()//1000000
        },
        cookies=cookies,
        headers={
            "Referer": url2
        }
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
    if r.url.startswith("https://jaccount.sjtu.edu.cn/jaccount/jalogin"):
        return None
    cookies = r.cookies
    for i in r.history:
        cookies.update(i.cookies)
    return cookies


def login_using_cookies(url, cookies):
    r = requests.get(
        url,
        headers={"accept-language": "zh-CN"},
        cookies=cookies
    )
    cookies.update(r.cookies)
    for i in r.history:
        cookies.update(i.cookies)
