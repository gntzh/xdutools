import json
import re
from base64 import b64encode
from pathlib import Path
from secrets import token_urlsafe

import requests
from lxml.etree import HTML
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def encrypt(key: str, value: str) -> str:
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv=token_urlsafe(12).encode())
    paddding = pad((token_urlsafe(48) + value).encode(), block_size=16)
    return b64encode(cipher.encrypt(paddding)).decode()


class Login:
    urls = {
        "ids": "http://ids.xidian.edu.cn/authserver/login",
        "apps": "http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp",
        "app": "http://ehall.xidian.edu.cn//appShow",
        "test": "http://ids.xidian.edu.cn/authserver/userAttributesEdit.do",
    }

    def __init__(self, username=None, password=None, cookies=None):
        self.username = username
        self.password = password
        self._session = requests.Session()
        self.session.headers.update(
            {
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,kk;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",  # noqa: E501
            }
        )
        if cookies:
            self.cookies.update(cookies)

    @property
    def session(self):
        return self._session

    def ids_get_tokens(self) -> tuple[dict[str, str], str]:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
            "Host": "ids.xidian.edu.cn",
            "Upgrade-Insecure-Requests": "1",
        }
        res = self.session.get(self.urls["ids"], headers=headers)
        if res.status_code == 200:
            html = HTML(res.text)
            return {
                i.xpath("@name")[0]: i.xpath("@value")[0]
                for i in html.xpath(
                    "//input[@type='hidden' and @value!='' and @name!='']"
                )
            }, html.xpath("//input[@id='pwdDefaultEncryptSalt']/@value")[0]
        raise Exception

    def ids_login(self):
        form_data, key = self.ids_get_tokens()
        form_data |= {
            "username": self.username,
            "password": encrypt(key, self.password),
            "rememberMe": "on",
        }
        res = self.session.post(
            "http://ids.xidian.edu.cn/authserver/login", data=form_data
        )
        if res.status_code == 200:
            return self.status

    @property
    def apps(self):
        res = self.session.get(self.urls["apps"])
        return res.json()["data"]

    def request_app(self, app_name):
        for i in self.apps:
            if i["appName"] == app_name:
                app_id = i["appId"]
                self.session.get(self.urls["app"], params={"appId": app_id})
                break

    @property
    def status(self):
        res = self.session.get(self.urls["test"], allow_redirects=False)
        if (
            res.status_code == 200
            and (m := re.search(r'userId=(?P<username>\d{11})"', res.text, re.S))
            is not None
        ):
            return m.group("username")

    @property
    def cookies(self):
        return self.session.cookies

    def save_cookies(self):
        path = Path.home() / ".xdutools"
        path.mkdir(exist_ok=True)
        (path / "cookies.json").write_text(json.dumps(self.session.cookies.get_dict()))

    @classmethod
    def by_cookies(cls):
        cookies = Path.home() / ".xdutools" / "cookies.json"
        cookies.touch()
        return cls(cookies=json.loads(cookies.read_text()))
