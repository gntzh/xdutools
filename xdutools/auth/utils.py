from httpx import AsyncClient


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
