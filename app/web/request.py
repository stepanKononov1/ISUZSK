import requests
from .reader import config
import json

proxies = {'https': 'http://127.0.0.1:8888'}


def query_post(exec, cookies):
    try:
        for key, value in cookies.items():
            if isinstance(value, dict):
                cookies[key] = json.dumps(value)
        url = f"https://{config.host.get_secret_value()}:{config.port.get_secret_value()}/{exec}"
        res = requests.post(url, cookies=cookies, proxies=proxies, timeout=30)
    except Exception as e:
        url = f"http://{config.host.get_secret_value()}:{config.port.get_secret_value()}/{exec}"
        res = requests.post(url, cookies=cookies, proxies=proxies, timeout=30)
    if isinstance(res.json(), dict):
        return res.json()
    else:
        return json.loads(res.json())
