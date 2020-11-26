from pathlib import Path

from asyncclick import get_app_dir


CWD: Path = Path.cwd()
APP_NAME = "XDU Tools"
APP_PATH = Path(get_app_dir(APP_NAME))
COOKIES_PATH = APP_PATH / "cookies"


def ensure_path():
    COOKIES_PATH.mkdir(parents=True, exist_ok=True)
