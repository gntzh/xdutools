from typing import Optional

from httpx import AsyncClient

from . import ids
from .types import ClientOrCookies, ClientOrCookiesT
from .utils import ccn2client, ccn2flag

LOG_IN_URL = "http://ehall.xidian.edu.cn//login"
APP_LIST_URL = "http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp"
USE_APP_URL = "http://ehall.xidian.edu.cn//appShow"


# TODO search app


async def get_app_list(coc: ClientOrCookies):
    async with ccn2client(coc) as client:
        res = await client.get(APP_LIST_URL)
        return res.json()["data"]


async def use_app(coc: ClientOrCookies, *, app_id: str):
    async with ccn2client(coc) as client:
        await client.get(USE_APP_URL, params={"appId": app_id})


async def use_app_by_name(
    coc: ClientOrCookies, app_name: str, app_list: list[dict] = None
):
    async with ccn2client(coc) as client:
        app_list = app_list or await get_app_list(client)
        for i in app_list:
            if i["appName"] == app_name:
                await use_app(client, app_id=i["appId"])
                break


async def get_logged_in_user(coc: ClientOrCookies) -> Optional[str]:
    async with ccn2client(coc) as client:
        res = await client.get("http://ehall.xidian.edu.cn/jsonp/userDesktopInfo.json")
        if res.status_code == 200 and (data := res.json())["hasLogin"]:
            return data["userId"]
        return None


async def log_in_with_ids(coc: ClientOrCookiesT) -> ClientOrCookiesT:
    async with ccn2flag(coc) as (client, is_client):
        await ids.log_in_service(client, service="http://ehall.xidian.edu.cn/login")
        if is_client:
            return client  # type:  ignore
        else:
            return client.cookies.jar  # type:  ignore


async def log_in(
    client: AsyncClient = None, *, username: str, password: str
) -> AsyncClient:
    client = await ids.log_in(
        client,
        username=username,
        password=password,
        service="http://ehall.xidian.edu.cn/login",
    )
    logged_in_user = await get_logged_in_user(client)
    if logged_in_user == username:
        return client
    raise Exception
