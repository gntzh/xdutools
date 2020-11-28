from http.cookiejar import CookieJar
from typing import TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:
    from httpx import AsyncClient

ClientOrCookies = Union["AsyncClient", CookieJar]

ClientOrCookiesT = TypeVar("ClientOrCookiesT", bound=ClientOrCookies)

ClientOrCookiesOrNone = Union[ClientOrCookies, None]
