from typing import Any

import asyncclick as click
from asyncclick.core import Context
from httpx import AsyncClient

from xdutools.apps.schedule import save_lessons_as_simple
from xdutools.auth import cookies, ehall, ids
from xdutools.auth.utils import create_client
from xdutools.state import COOKIES_PATH, ensure_path

ensure_path()
click.anyio_backend = "asyncio"


@click.group()
@click.pass_context
@click.option("--username", "-U", "username", default=None)
@click.option("--password", "-P", "password", default=None)
def main(ctx: Context, username: str = None, password: str = None):
    ctx.ensure_object(dict)
    ctx.obj["username"] = username
    ctx.obj["password"] = password


@main.resultcallback()
@click.pass_context
async def shutdown(ctx: Context, *arg, **kw):
    client: AsyncClient = ctx.obj.get("client")
    if client:
        cookies.save_cookies_to_file(
            client.cookies, COOKIES_PATH / ctx.obj.get("username")
        )
        await client.aclose()


@main.command()
@click.argument("name", default="world")
def hello(name):
    click.secho(f"Hello, {name}!", fg="green")


@click.pass_context
def set_value(ctx: Context, *, key: Any, text=None, kw: dict = {}) -> Any:
    if (value := ctx.obj.get(key)) is None:
        value = click.prompt(text or key, **kw)
        ctx.obj[key] = value
    return value


@click.pass_context
async def log_in_ids(ctx: Context) -> AsyncClient:
    username: str = set_value(key="username", text="账号")
    jar = cookies.load_cookies_from_file(COOKIES_PATH / username)
    client = create_client(cookies=jar)
    if jar:
        u = await ids.get_logged_in_user(client)
        if u == username:
            return client
    password: str = ctx.obj.get("password") or click.prompt("密码")
    await ids.log_in(client, username=username, password=password)
    return client


@click.pass_context
async def log_in_ehall(ctx: Context) -> AsyncClient:
    username: str = set_value(key="username", text="账号")
    jar = cookies.load_cookies_from_file(COOKIES_PATH / username)
    client = create_client(cookies=jar)
    if jar:
        u = await ehall.get_logged_in_user(client)
        if u == username:
            ctx.obj["client"] = client
            return client
        if u is None:
            u = await ids.get_logged_in_user(client)
            if u == username:
                await ehall.log_in_with_ids(client)
                ctx.obj["client"] = client
                return client
    password: str = set_value(key="password", text="密码")
    await ehall.log_in(client, username=username, password=password)
    ctx.obj["client"] = client
    return client


@main.command()
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(("simple", "default", "wakeup")),
    default="default",
)
@click.pass_context
async def schedule(ctx: Context, fmt: str):
    client = await log_in_ehall()
    from xdutools.apps.schedule import (E_HALL_ID, get_lessons,
                                        save_lessons_as_wake_up)
    from xdutools.auth.ehall import use_app

    await use_app(client, app_id=E_HALL_ID)
    lessons = await get_lessons(client)
    if fmt == "wakeup":
        save_lessons_as_wake_up(lessons)
    elif fmt == "simple":
        save_lessons_as_simple(lessons)
    else:
        save_lessons_as_wake_up(lessons)


if __name__ == "__main__":
    main()
