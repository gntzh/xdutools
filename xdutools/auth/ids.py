import re
from base64 import b64encode
from secrets import token_urlsafe
from typing import TYPE_CHECKING, Optional

from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from .utils import create_client

if TYPE_CHECKING:
    from httpx import AsyncClient

    # TODO Client 和 CookiesLike 兼容参数

LOG_IN_URL = "http://ids.xidian.edu.cn/authserver/login"
STATUS_URL = "http://ids.xidian.edu.cn/authserver/userAttributesEdit.do"


def encrypt(key: str, value: str) -> str:
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv=token_urlsafe(12).encode())
    paddding = pad((token_urlsafe(48) + value).encode(), block_size=16)
    return b64encode(cipher.encrypt(paddding)).decode()


async def get_logged_in_user(client: "AsyncClient") -> Optional[str]:
    res = await client.get(STATUS_URL)
    if (
        res.status_code == 200
        and (m := re.search(r'userId=(?P<username>\d{11})"', res.text, re.S))
        is not None
    ):
        return m.group("username")
    return None


async def get_key_and_hidden_fields(client: "AsyncClient" = None) -> tuple[str, dict]:
    if client is None:
        client = create_client()
        flag = True
    flag = False
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
        "Host": "ids.xidian.edu.cn",
        "Upgrade-Insecure-Requests": "1",
    }
    res = await client.get(LOG_IN_URL, headers=headers)
    if flag:
        await client.aclose()
    if res.status_code == 200:
        page = BeautifulSoup(res.text)
        return page.select_one("#pwdDefaultEncryptSalt")["value"], {
            el.get("name"): el.get("value")
            for el in page.select("input[type='hidden'][name][value]:not([name=''])")
        }
    else:
        raise Exception


async def log_in(
    username: str, password: str, client: "AsyncClient" = None
) -> "AsyncClient":
    client = client or create_client()
    key, form_data = await get_key_and_hidden_fields(client)
    form_data |= {
        "username": username,
        "password": encrypt(key, password),
        "rememberMe": "on",
    }
    res = await client.post("http://ids.xidian.edu.cn/authserver/login", data=form_data)
    if res.status_code == 200:
        logged_in_user = await get_logged_in_user(client)
        if logged_in_user and logged_in_user == username:
            return client
    raise Exception
