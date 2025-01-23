import requests
from .reader import config

proxies = {'https': 'http://127.0.0.1:8888'}


def query_post(exec, cookies):
    try:
        url = f"https://{config.host.get_secret_value()}:{config.port.get_secret_value()}/{exec}"
        res = requests.post(url, cookies=cookies, proxies=proxies)
    except:
        url = f"http://{config.host.get_secret_value()}:{config.port.get_secret_value()}/{exec}"
        res = requests.post(url, cookies=cookies, proxies=proxies)
    return res.json()
