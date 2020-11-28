from typing import Optional

from httpx import AsyncClient
from xdutools.auth.types import ClientOrCookies

from .utils import ccn2client, create_client


async def get_logged_in_user(coc: ClientOrCookies) -> Optional[str]:
    async with ccn2client(coc) as client:
        res = await client.get("https://xxcapp.xidian.edu.cn/uc/wap/user/get-info")
        if res.status_code == 200 and (data := res.json())["m"] == "操作成功":
            return data["d"]["base"]["role"]["number"]
        return None


async def log_in(
    client: AsyncClient = None, *, username: str, password: str, redirect: str = None
) -> AsyncClient:
    client = client or create_client()
    res = await client.post(
        "https://xxcapp.xidian.edu.cn/uc/wap/login/check",
        data={"username": username, "password": password},
        params={"redirect": redirect},
    )
    if res.status_code == 200:
        logged_in_user = await get_logged_in_user(client)
        if logged_in_user and logged_in_user == username:
            return client
    raise Exception
