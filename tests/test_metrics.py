from threading import Thread

from src import constants, metrics

DICTIONARY = "fr-it"
FILE = "kobo"


def test_file_error() -> None:
    constants.METRICS.write_text("")
    assert not metrics.read()


def test_new_dictionary() -> None:
    metrics.plus_one(DICTIONARY, FILE, "full")
    assert metrics.read() == {DICTIONARY: {FILE: {"full": 1}}}


def test_new_file() -> None:
    metrics.write({DICTIONARY: {"some": {"full": 10}}})
    metrics.plus_one(DICTIONARY, FILE, "full")
    assert metrics.read() == {DICTIONARY: {FILE: {"full": 1}, "some": {"full": 10}}}


def test_new_etym() -> None:
    metrics.write({DICTIONARY: {FILE: {"full": 5}}})
    metrics.plus_one(DICTIONARY, FILE, "noetym")
    assert metrics.read() == {DICTIONARY: {FILE: {"full": 5, "noetym": 1}}}


def test_normal() -> None:
    metrics.write({DICTIONARY: {FILE: {"full": 41}}})
    metrics.plus_one(DICTIONARY, FILE, "full")
    assert metrics.read() == {DICTIONARY: {FILE: {"full": 42}}}


def test_concurrent_access() -> None:
    count = 500

    def function() -> None:
        metrics.plus_one(DICTIONARY, FILE, "full")

    assert not metrics.read()

    threads = [Thread(target=function) for _ in range(count)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert metrics.read() == {DICTIONARY: {FILE: {"full": count}}}
