from websocket import create_connection
import requests
from PIL import Image
import io
import json
import threading


def wss_monitor(wss, update_qr_code_callback, login_callback):
    while True:
        try:
            r = wss.recv()
        except Exception:
            break
        if not r:
            break
        j = json.loads(r)
        t = j["type"]
        if t == "UPDATE_QR_CODE":
            p = j["payload"]
            sig = p["sig"]
            ts = p["ts"]
            update_qr_code_callback(ts, sig)
        elif t == "LOGIN":
            login_callback()
            break


def get_wss(uuid, cookies, update_qr_code_callback, login_callback):
    cookie = "; ".join(
        [
            f"{k}={v}"
            for k, v in cookies.get_dict(
                domain="jaccount.sjtu.edu.cn"
            ).items()
        ]
    )
    wss = create_connection(
        f"wss://jaccount.sjtu.edu.cn/jaccount/sub/{uuid}",
        header={
            "cookie": cookie
        }
    )
    t = threading.Thread(
        target=wss_monitor,
        args=(
            wss, update_qr_code_callback, login_callback
        )
    )
    t.start()
    return wss, t


def send_update_qr_code(wss):
    wss.send('{ "type": "UPDATE_QR_CODE" }')


def get_qr_code_img(uuid, ts, sig, cookies):
    r = requests.get(
        "https://jaccount.sjtu.edu.cn/jaccount/qrcode",
        params={
            "uuid": uuid,
            "ts": ts,
            "sig": sig
        },
        cookies=cookies
    )
    img = Image.open(io.BytesIO(r.content))
    return img


def qr_code_login(uuid, cookies):
    r = requests.get(
        "https://jaccount.sjtu.edu.cn/jaccount/expresslogin",
        params={"uuid": uuid},
        cookies=cookies
    )
    if r.url.startswith("https://jaccount.sjtu.edu.cn/jaccount/expresslogin"):
        return None
    cookies = r.cookies
    for i in r.history:
        cookies.update(i.cookies)
    return cookies
