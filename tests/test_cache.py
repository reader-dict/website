import time
from unittest.mock import patch

import pytest

from src import cache, constants


def test_add() -> None:
    uid = cache.add("", "", "fr", "it", "dicthtml-fr-it.zip", "kobo")
    assert (constants.FILES_CACHE / cache.cache_key(uid)).is_file()
    assert (constants.FILES_CACHE / cache.cache_key(uid)).read_text() == "||fr|it|dicthtml-fr-it.zip|kobo"


def test_add_notimer() -> None:
    uid = cache.add_notimer("some", "thing")
    assert (constants.FILES_CACHE / cache.cache_key(uid)).is_file()
    assert (constants.FILES_CACHE / cache.cache_key(uid)).read_text() == "thing"


def test_get() -> None:
    uid = cache.add("order-type", "order-id", "fr", "it", "dicthtml-fr-it.zip", "kobo")
    assert cache.get(uid) == ["order-type", "order-id", "fr", "it", "dicthtml-fr-it.zip", "kobo"]


def test_get_notimer() -> None:
    uid = cache.add_notimer("some", "thing")
    assert cache.get_notimer(uid) == "thing"


def test_remove() -> None:
    uid = cache.add("", "", "fr", "it", "dicthtml-fr-it.zip", "kobo")
    assert (constants.FILES_CACHE / cache.cache_key(uid)).is_file()

    cache.remove(uid)
    assert not (constants.FILES_CACHE / cache.cache_key(uid)).is_file()


def test_miss() -> None:
    with pytest.raises(cache.CacheMissError):
        cache.get("some-uid")


def test_expiration() -> None:
    with patch.object(constants, "DELAY_BEFORE_EXPIRATION_IN_SEC", new=0.001):
        uid = cache.add("", "", "fr", "it", "dicthtml-fr-it.zip", "kobo")

    time.sleep(0.1)
    with pytest.raises(cache.CacheExpiredError):
        cache.get(uid)

    # The entry was purged from the cache
    assert not (constants.FILES_CACHE / str(uid)).is_file()
