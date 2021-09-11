from base64 import b64encode
from secrets import token_urlsafe
from typing import Optional

from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from httpx import AsyncClient

from .types import ClientOrCookies, ClientOrCookiesT
from .utils import ccn2client, ccn2flag, create_client

# TODO Client 和 CookiesLike 兼容参数


def encrypt(key: str, value: str) -> str:
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv=token_urlsafe(12).encode())
    paddding = pad((token_urlsafe(48) + value).encode(), block_size=16)
    return b64encode(cipher.encrypt(paddding)).decode()


async def get_logged_in_user(coc: ClientOrCookies) -> Optional[str]:
    async with ccn2client(coc) as client:
        res = await client.get(
            "https://ids.xidian.edu.cn/personalInfo/common/getUserConf"
        )
        if res.status_code == 200 and (data := res.json()).get("code") == "0":
            return data["datas"]["uid"]
        return None


async def get_key_and_hidden_fields(con: AsyncClient = None) -> tuple[str, dict]:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
        "Host": "ids.xidian.edu.cn",
        "Upgrade-Insecure-Requests": "1",
    }
    async with ccn2client(con) as client:
        res = await client.get(
            "http://ids.xidian.edu.cn/authserver/login",
            params={"type": "userNameLogin"},
            headers=headers,
        )
        if res.status_code == 200:
            page = BeautifulSoup(res.text)
            return page.select_one("#pwdEncryptSalt")["value"], {
                el.get("name"): el.get("value")
                for el in page.select(
                    ".loginFromClass input[type='hidden'][name][value]:not([name=''])"
                )
            }
        else:
            raise Exception


async def log_in_service(coc: ClientOrCookiesT, *, service: str) -> ClientOrCookiesT:
    client = coc or create_client(cookies=coc)
    async with ccn2flag(coc) as (client, is_client):
        await client.get(
            "http://ids.xidian.edu.cn/authserver/login",
            params={"service": service},
        )
        if is_client:
            return client  # type: ignore
        else:
            return client.cookies.jar  # type: ignore


async def log_in(
    client: AsyncClient = None, *, username: str, password: str, service: str = None
) -> AsyncClient:
    client = client or create_client()
    key, form_data = await get_key_and_hidden_fields(client)
    form_data |= {  # type: ignore[operator]
        "username": username,
        "password": encrypt(key, password),
        "rememberMe": "on",
    }
    res = await client.post(
        "http://ids.xidian.edu.cn/authserver/login",
        data=form_data,
        params={"service": service},
    )
    # FIXME post 重定向到了
    # ids.xidian.edu.cn/authserver/services/j_spring_cas_security_check
    if res.status_code == 200:
        res = await client.get(
            "http://ids.xidian.edu.cn/authserver/login",
            params={"service": service},
        )
        if res.status_code == 200:
            logged_in_user = await get_logged_in_user(client)
            if logged_in_user and logged_in_user == username:
                return client
    raise Exception
