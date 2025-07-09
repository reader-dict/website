import hashlib
from datetime import UTC, datetime, timedelta

import ulid

from src import constants


class CacheError(Exception):
    pass


class CacheExpiredError(CacheError):
    pass


class CacheMissError(CacheError):
    pass


def add(order_type: str, order_id: str, lang_src: str, lang_dst: str, file_name: str, fmt: str) -> str:  # noqa: PLR0913
    expiration_date = datetime.now(tz=UTC) + timedelta(seconds=constants.DELAY_BEFORE_EXPIRATION_IN_SEC)
    uid = ulid.ULID.from_datetime(expiration_date).hex
    return add_notimer(uid, f"{order_type}|{order_id}|{lang_src}|{lang_dst}|{file_name}|{fmt}")


def add_notimer(key: str, value: str) -> str:
    constants.FILES_CACHE.mkdir(exist_ok=True)
    (constants.FILES_CACHE / cache_key(key)).write_text(value)
    return key


def cache_key(key: str | ulid.ULID) -> str:
    return hashlib.md5(str(key).encode(), usedforsecurity=False).hexdigest()


def get(key: str) -> list[str]:
    cached = get_notimer(key)
    now = datetime.now(tz=UTC)
    entry_expiration = ulid.ULID.from_hex(key).datetime
    if entry_expiration <= now:
        remove(key)
        raise CacheExpiredError from None

    return cached.split("|")


def get_notimer(key: str) -> str:
    try:
        return (constants.FILES_CACHE / cache_key(key)).read_text()
    except FileNotFoundError:
        raise CacheMissError from None


def remove(key: str) -> None:
    (constants.FILES_CACHE / cache_key(key)).unlink(missing_ok=True)
