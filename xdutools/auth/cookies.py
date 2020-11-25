from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from http.cookiejar import CookieJar

    from httpx import Cookies


def save_cookies_to_file(cookies: "Cookies", path: Path):
    jar = MozillaCookieJar(path)
    for i in cookies.jar:
        jar.set_cookie(i)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
    jar.save(ignore_discard=True)


def load_cookies_from_file(path: Path) -> "CookieJar":
    jar = MozillaCookieJar(path)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        jar.save(ignore_discard=True)
    else:
        jar.load()
    return jar
