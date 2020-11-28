from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from httpx import Cookies


def save_cookies_to_file(cookies: "Cookies", path: Path):
    jar = MozillaCookieJar(path)
    for i in cookies.jar:
        jar.set_cookie(i)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
    jar.save(ignore_discard=True)


def load_cookies_from_file(path: Path) -> Union[MozillaCookieJar, None]:
    if path.is_file():
        jar = MozillaCookieJar(path)
        jar.load(ignore_discard=True)
        return jar
    else:
        return None
