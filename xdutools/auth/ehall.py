from typing import Optional, TYPE_CHECKING

from . import ids

if TYPE_CHECKING:
    from httpx import AsyncClient


LOG_IN_URL = "http://ehall.xidian.edu.cn//login"
APP_LIST_URL = "http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp"
USE_APP_URL = "http://ehall.xidian.edu.cn//appShow"


async def get_app_list(client: "AsyncClient"):
    res = await client.get(APP_LIST_URL)
    return res.json()["data"]


# search app


async def use_app(client: "AsyncClient", app_id: str):
    await client.get(USE_APP_URL, params={"appId": app_id})


async def use_app_by_name(
    client: "AsyncClient", app_name: str, app_list: list[dict] = None
):
    app_list = app_list or await get_app_list(client)
    for i in app_list:
        if i["appName"] == app_name:
            await use_app(i["appId"])
            break


async def log_in_with_ids(client: "AsyncClient"):
    await ids.login_in_service(client, service="http://ehall.xidian.edu.cn/login")


async def log_in(
    username: str, password: str, *, client: "AsyncClient" = None
) -> "AsyncClient":
    client = await ids.log_in(
        username,
        password,
        service="http://ehall.xidian.edu.cn/login",
    )
    return client


async def get_logged_in_user(client: "AsyncClient") -> Optional[str]:
    res = await client.get("http://ehall.xidian.edu.cn/jsonp/userDesktopInfo.json")
    if res.status_code == 200 and (data := res.json())["hasLogin"]:
        return data["userId"]
    return None
