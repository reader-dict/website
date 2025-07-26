import imaplib
import json
import smtplib
from unittest.mock import MagicMock, patch

import pytest
import ulid

from src import constants, utils
from src.models import Order

from .payloads import PLAN_ID


def test_craft_tmp_downloads_url() -> None:
    dictionary = utils.load_dictionaries()["eo"]["fr"]
    links = utils.craft_downloads_url(dictionary)
    assert links.keys() == constants.DICTIONARY_FORMATS.keys()
    assert links["kobo"][:3] == ("Kobo", "dicthtml-eo-fr.zip", "dicthtml-eo-fr-noetym.zip")
    assert links["mobi"][:3] == ("Kindle", "dict-eo-fr.mobi.zip", "dict-eo-fr-noetym.mobi.zip")
    assert links["stardict"][:3] == ("StarDict", "dict-eo-fr.zip", "dict-eo-fr-noetym.zip")
    assert links["df"][:3] == ("DictFile", "dict-eo-fr.df.bz2", "dict-eo-fr-noetym.df.bz2")
    assert links["dictorg"][:3] == ("DICT.org", "dictorg-eo-fr.zip", "dictorg-eo-fr-noetym.zip")
    for link in links.values():
        for idx in [3, 4]:
            assert ulid.ULID.from_hex(link[idx]).hex == link[idx]


def test_craft_tmp_downloads_url_missing_format() -> None:
    dictionary = utils.load_dictionaries()["eo"]["fr"]
    dictionary["formats"] = str(dictionary["formats"]).replace(",mobi", "")
    links = utils.craft_downloads_url(dictionary)
    assert len(links.keys()) == len(constants.DICTIONARY_FORMATS.keys()) - 1
    assert "mobi" not in links


def test_get_dictionary_from_langs() -> None:
    assert utils.get_dictionary_from_langs("eo-fr")


@pytest.mark.parametrize("langs_pair", ["", "eo", "eo-unknown"])
def test_get_dictionary_from_langs_unknown(langs_pair: str) -> None:
    assert not utils.get_dictionary_from_langs(langs_pair)


def test_get_dictionary_from_key() -> None:
    assert utils.get_dictionary_from_key("plan_id", PLAN_ID)["name"] == "eo-fr"


def test_get_dictionary_from_key_unknown() -> None:
    assert not utils.get_dictionary_from_key("plan_id", "unknown")


def test_get_dictionary_metadata() -> None:
    assert utils.get_dictionary_metadata("eo", "fr")


@pytest.mark.parametrize(
    ("lang", "name", "expected"),
    [
        ("fr", "dicthtml-fr-fr.zip", "kobo"),
        ("fr", "dicthtml-fr-fr-noetym.zip", "kobo"),
        ("fr", "dict-fr-fr.mobi.zip", "mobi"),
        ("fr", "dict-fr-fr-noetym.mobi.zip", "mobi"),
        ("fr", "dict-fr-fr.zip", "stardict"),
        ("fr", "dict-fr-fr-noetym.zip", "stardict"),
        ("fr", "dict-fr-fr.df.bz2", "df"),
        ("fr", "dict-fr-fr-noetym.df.bz2", "df"),
        ("fr", "dictorg-fr-fr.zip", "dictorg"),
        ("fr", "dictorg-fr-fr-noetym.zip", "dictorg"),
    ],
)
def test_get_format_from_file_name(lang: str, name: str, expected: str) -> None:
    assert utils.get_format_from_file_name(lang, name) == expected


@pytest.mark.parametrize(
    ("lang", "name"),
    [
        ("fr", "zz"),
        ("eo", "/etc/passwd"),
        ("eo", "dicthtml-eo-fr.zip"),
    ],
)
def test_get_format_from_file_name_bad(lang: str, name: str) -> None:
    with pytest.raises(FileNotFoundError):
        utils.get_format_from_file_name(lang, name)


def test_is_checkpoint() -> None:
    assert utils.is_checkpoint("1" * 64)


@pytest.mark.parametrize("checkpoint", ["", "aaa", "t" * 64])
def test_is_checkpoint_false(checkpoint: str) -> None:
    assert not utils.is_checkpoint(checkpoint)


def test_load_dictionaries() -> None:
    dictionaries = {
        "fr": {
            "fr": {
                "enabled": True,
                "formats": "df,dictorg,kobo,mobi,stardict",
                "plan_id": "plan-id",
                "price": 9.49,
                "price_purchase": 19.49,
                "progress": "done",
                "uid": "uid",
                "updated": "2025-04-04",
                "words": 2053016,
            },
            "fro": {
                "enabled": False,
                "formats": "df,dictorg,kobo,mobi,stardict",
                "plan_id": "plan-id",
                "price": 9.49,
                "price_purchase": 19.49,
                "progress": "format:mobi",
                "uid": "uid",
                "updated": "2025-04-04",
                "words": 189856,
            },
        }
    }
    constants.DICTIONARIES.write_text(json.dumps(dictionaries))
    data = utils.load_dictionaries()

    assert len(data) == 1
    for details in data["fr"].values():
        assert sorted(details.keys()) == sorted(constants.DICTIONARY_KEYS_ALL)


def test_load_orders() -> None:
    order = Order("some-id", dictionary="eo-fr", source="paypal", plan_id="plan-id", ulid="ulid")
    assert not utils.load_orders()
    utils.store_order(order)
    assert utils.load_orders() == {"some-id": order}


def test_send_email_no_address(caplog: pytest.LogCaptureFixture) -> None:
    assert not utils.send_email(Order("some-id"))

    assert [record.getMessage() for record in caplog.records] == [
        "[email order ID='some-id'] No email address provided!",
    ]


def test_send_email_no_smtp_password(caplog: pytest.LogCaptureFixture) -> None:
    order = Order(
        "some-id",
        user="Alice",
        email="alice@example.org",
        dictionary="eo-fr",
        source="paypal",
        plan_id="plan-id",
        ulid="ulid",
    )

    with (
        patch.object(smtplib, "SMTP_SSL", MagicMock()) as mocked_s,
        patch.object(imaplib, "IMAP4_SSL", MagicMock()) as mocked_i,
    ):
        assert not utils.send_email(order)
        mocked_s.assert_not_called()
        mocked_i.assert_not_called()

    assert [record.getMessage() for record in caplog.records] == [
        "[email order ID='some-id'] No SMTP password defined! Email saved but not sent.",
    ]


def test_send_email_smtp_error(caplog: pytest.LogCaptureFixture) -> None:
    order = Order(
        "some-id",
        user="Alice",
        email="alice@example.org",
        dictionary="eo-fr",
        source="paypal",
        plan_id="plan-id",
        ulid="ulid",
    )

    with (
        patch.object(constants, "SMTP_PASSWORD", "s3cr37"),
        patch.object(smtplib, "SMTP_SSL", MagicMock(side_effect=ValueError("boom"))) as mocked_s,
        patch.object(imaplib, "IMAP4_SSL", MagicMock()) as mocked_i,
    ):
        assert not utils.send_email(order)
        mocked_s.assert_called_once()
        mocked_i.assert_called_once()

    assert [record.getMessage().split("\n", 1)[0] for record in caplog.records] == [
        "[email order ID='some-id'] Could not send the email to Alice at alice@example.org!",
        "[email order ID='some-id'] Kept an email copy.",
    ]


def test_send_email_imap_error(caplog: pytest.LogCaptureFixture) -> None:
    order = Order(
        "some-id",
        user="Alice",
        email="alice@example.org",
        dictionary="eo-fr",
        source="paypal",
        plan_id="plan-id",
        ulid="ulid",
    )

    with (
        patch.object(constants, "SMTP_PASSWORD", "s3cr37"),
        patch.object(smtplib, "SMTP_SSL", MagicMock()) as mocked_s,
        patch.object(imaplib, "IMAP4_SSL", MagicMock(side_effect=ValueError("boom"))) as mocked_i,
    ):
        assert not utils.send_email(order)
        mocked_s.assert_called_once()
        mocked_i.assert_called_once()

    assert [record.getMessage().split("\n", 1)[0] for record in caplog.records] == [
        "[email order ID='some-id'] Email sent to Alice at alice@example.org",
        "[email order ID='some-id'] Could not keep a copy of the email sent to Alice at alice@example.org!",
    ]


def test_send_email(caplog: pytest.LogCaptureFixture) -> None:
    order = Order(
        "some-id",
        user="Alice",
        email="alice@example.org",
        dictionary="eo-fr",
        source="paypal",
        plan_id="plan-id",
        ulid="ulid",
    )

    with (
        patch.object(constants, "SMTP_PASSWORD", "s3cr37"),
        patch.object(smtplib, "SMTP_SSL", MagicMock()) as mocked_s,
        patch.object(imaplib, "IMAP4_SSL", MagicMock()) as mocked_i,
    ):
        assert utils.send_email(order)
        mocked_s.assert_called_once()
        mocked_i.assert_called_once()

    assert [record.getMessage() for record in caplog.records] == [
        "[email order ID='some-id'] Email sent to Alice at alice@example.org",
        "[email order ID='some-id'] Kept an email copy.",
    ]


def test_store_order_updated() -> None:
    order1 = Order("some-id", dictionary="eo-fr", source="paypal", plan_id="plan-id", status="active", ulid="ulid")
    order2 = Order("some-id2", dictionary="eo-fr", source="paypal", plan_id="plan-id2", ulid="ulid2")
    assert not utils.load_orders()
    utils.store_order(order1)
    utils.store_order(order2)
    assert utils.load_orders() == {"some-id": order1, "some-id2": order2}

    order1.dictionary_override = "eo-eo"
    order1.user = "Alice"
    order1.status = "cancelled"
    order1.status_update_time = "2025-05-30T19:59:05Z"

    utils.store_order(order1)
    orders = utils.load_orders()
    assert orders == {"some-id": order1, "some-id2": order2}

    first_order = orders["some-id"]
    assert first_order.dictionary_override == "eo-eo"
    assert first_order.status_update_time == "2025-05-30T19:59:05Z"
    assert first_order.user == "Alice"


def test_language() -> None:
    assert utils.language("all") == "Universal"


def test_language_missing() -> None:
    assert utils.language("unknown") == "unknown"
