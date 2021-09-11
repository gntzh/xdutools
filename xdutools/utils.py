from datetime import datetime, timedelta, timezone

Beijing = timezone(timedelta(hours=8))


def utc_now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def now() -> datetime:
    return utc_now().astimezone(Beijing)
