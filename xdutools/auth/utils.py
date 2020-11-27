from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

from httpx import AsyncClient

from .types import ClientOrCookiesOrNone


def create_client(*args, **kwargs) -> AsyncClient:
    client = AsyncClient(*args, **kwargs)
    client.headers.update(
        {
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,kk;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",  # noqa: E501
        }
    )
    return client


# XXX contexlib.asynccontextmanager 类型标注没有被 Pylance 提示（MyPy 可以检查
# XXX 函数风格混乱


@asynccontextmanager
async def ccn2client(
    ccn: ClientOrCookiesOrNone, *args, **kwargs
) -> AsyncIterator[AsyncClient]:
    try:
        if is_client := isinstance(ccn, AsyncClient):
            client = ccn
            is_client = True
        elif ccn is None:
            client = create_client(*args, **kwargs)
        else:
            client = create_client(cookies=ccn, *args, **kwargs)
        yield client  # type: ignore
    finally:
        if not is_client:
            await client.aclose()  # type: ignore


@asynccontextmanager
async def ccn2flag(
    ccn: ClientOrCookiesOrNone, *args, **kwargs
) -> AsyncIterator[tuple[AsyncClient, Optional[bool]]]:
    """
    Returns:
        1. client
        2. flag:
            - `True`: Client
            - `False`: Cookies
            - `None`: None
    """
    try:
        flag = None
        if flag := isinstance(ccn, AsyncClient):
            client = ccn
        elif ccn is None:
            flag = ccn
            client = create_client(*args, **kwargs)
        else:
            client = create_client(cookies=ccn, *args, **kwargs)
        yield client, flag  # type: ignore
    finally:
        if not flag:
            await client.aclose()  # type: ignore
