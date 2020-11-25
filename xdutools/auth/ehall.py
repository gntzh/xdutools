from httpx import AsyncClient


APP_LIST_URL = "http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp"
USE_APP_URL = "http://ehall.xidian.edu.cn//appShow"


async def get_app_list(client: AsyncClient):
    res = await client.get(APP_LIST_URL)
    return res.json()["data"]


async def use_app(client: AsyncClient, app_id: str):
    res = await client.get(USE_APP_URL, params={"appId": app_id})
    return res


async def use_app_by_name(
    client: AsyncClient, app_name: str, app_list: list[dict] = None
):
    app_list = app_list or await get_app_list(client)
    for i in app_list:
        if i["appName"] == app_name:
            await use_app(i["appId"])
            break
