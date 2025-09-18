import json
from collections.abc import Generator
from copy import deepcopy

import bottle
import bottle_file_cache
import pytest
import responses
from webtest import TestApp

from src import constants, server, utils

from .payloads import (
    ORDER_P,
    ORDER_S,
    PAYPAL_WEBHOOK_HEADERS,
    PAYPAL_WEBHOOK_PAYLOAD,
    PURCHASE_ID,
    STRIPE_WEBHOOK_HEADERS,
    STRIPE_WEBHOOK_PAYLOAD,
    SUBSCRIPTION_ID,
)

CHECKPOINT_BAD = "0" * 64


@pytest.fixture(scope="session")
def app() -> TestApp:
    return TestApp(server.app)


def checkpoint_good(order_id: str) -> str:
    return utils.load_orders()[order_id].checkpoint


def test_client_ip() -> None:
    assert server.client_ip() == "unknown"


def test_api_dictionary_get(app: TestApp) -> None:
    for should_be_cached in [False, True]:
        response = app.get(constants.ROUTE_API_DICT)
        assert json.loads(response.body) == utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_MINIMAL)
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


@responses.activate()
def test_api_webhook_paypal(app: TestApp, mock_responses: Generator, caplog: pytest.LogCaptureFixture) -> None:
    app.post(constants.ROUTE_API_WEBHOOK_PAYPAL, PAYPAL_WEBHOOK_PAYLOAD, headers=PAYPAL_WEBHOOK_HEADERS, status=200)
    assert (
        "Webhook order handled"
        in [record.getMessage().split("\n", 1)[0] for record in caplog.records if record.levelname == "INFO"][-1]
    )

    caplog.clear()
    app.post(
        constants.ROUTE_API_WEBHOOK_PAYPAL,
        PAYPAL_WEBHOOK_PAYLOAD + b"more data",
        headers=PAYPAL_WEBHOOK_HEADERS,
        status=200,
    )
    assert [record.getMessage().split("\n", 1)[0] for record in caplog.records if record.levelname == "ERROR"] == [
        "[paypal] Webhook signature failed",
    ]


@responses.activate()
def test_api_webhook_stripe(app: TestApp, mock_responses: Generator, caplog: pytest.LogCaptureFixture) -> None:
    app.post(constants.ROUTE_API_WEBHOOK_STRIPE, STRIPE_WEBHOOK_PAYLOAD, headers=STRIPE_WEBHOOK_HEADERS, status=200)
    assert (
        "Webhook order handled"
        in [record.getMessage().split("\n", 1)[0] for record in caplog.records if record.levelname == "INFO"][-1]
    )

    caplog.clear()
    app.post(
        constants.ROUTE_API_WEBHOOK_STRIPE,
        STRIPE_WEBHOOK_PAYLOAD + b"more data",
        headers=STRIPE_WEBHOOK_HEADERS,
        status=200,
    )
    assert [record.getMessage().split("\n", 1)[0] for record in caplog.records if record.levelname == "ERROR"] == [
        "[stripe] Webhook signature failed",
    ]


@responses.activate()
def test_api_pre_order(app: TestApp, mock_responses: Generator, caplog: pytest.LogCaptureFixture) -> None:
    app.get(f"{constants.ROUTE_API_PRE_ORDER}/a/b", status=200)

    msg = "[/pre-order] Client reference ID '01K4D2WZR8G1TG36RNF3020124-eo-fr' from IP 'unknown'"
    assert [record.getMessage() for record in caplog.records if record.levelname == "INFO"][-1] == msg


@pytest.mark.parametrize(
    ("kind", "file"),
    [
        ("font", "InterVariable.woff2"),
        ("img", "favicon.svg"),
        ("style", "home.css"),
        ("script", "home.js"),
    ],
)
def test_asset(kind: str, file: str, app: TestApp) -> None:
    response = app.get(f"/asset/{kind}/{file}")
    assert response.body_file


@pytest.mark.parametrize(
    ("kind", "file"),
    [
        ("img", "unknown.webp"),
        ("style", "unknown.css"),
        ("script", "unknown.js"),
        ("unknown", "/etc/passwd"),
    ],
)
def test_asset_not_found(kind: str, file: str, app: TestApp) -> None:
    response = app.get(f"/asset/{kind}/{file}", status=404)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "status",
    [
        "400 Bad Request",
        "403 Forbidden",
        "404 Not Found",
        "410 Gone",
        "999 Unknown",
    ],
)
def test_custom_error(status: str) -> None:
    error = bottle.HTTPError(status)
    assert "Whoopsy" in server.custom_error(error)


@responses.activate()
def test_downloads_bilingual_no_order_id(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_no_checkpoint(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", params={"order": "uid"}, status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_invalid_checkpoint(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", params={"checkpoint": "bad", "order": "uid"}, status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_unknown_dictionary(
    app: TestApp, caplog: pytest.LogCaptureFixture, mock_responses: Generator
) -> None:
    utils.store_order(ORDER_S)
    app.get(
        "/download/zz/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=404,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] The dictionary zz-fr does not exist, or is disabled (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_no_order_found(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", params={"checkpoint": CHECKPOINT_BAD, "order": "uid"}, status=404)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download order ID='uid'] No order with that ID"
    )


@responses.activate()
def test_downloads_bilingual_checkpoints_mismatch(
    app: TestApp, caplog: pytest.LogCaptureFixture, mock_responses: Generator
) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    app.get("/download/eo/fr", params={"checkpoint": CHECKPOINT_BAD, "order": SUBSCRIPTION_ID}, status=403)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] Checkpoint '{CHECKPOINT_BAD}' is invalid (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_subscription_status_not_ok(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    order.status = "cancelled"
    utils.store_order(order)

    app.get(
        "/download/eo/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=403,
    )
    assert (
        "Status does not allow to continue"
        in [record.getMessage() for record in caplog.records if record.levelname == "INFO"][-1]
    )


@responses.activate()
def test_downloads_bilingual_dictionaries_inexistant(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    utils.store_order(ORDER_S)

    app.get(
        "/download/all/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=404,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] The dictionary all-fr does not exist, or is disabled (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_dictionaries_mismatch(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    app.get(
        "/download/eo/eo",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=403,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] Dictionary mismatch: requested='eo-eo', available='eo-fr' (from unknown)"
    )


@responses.activate()
def test_downloads_bilingual_purchase_dictionary(app: TestApp, mock_responses: Generator) -> None:
    utils.store_order(ORDER_P)

    response = app.get("/download/eo/fr", params={"checkpoint": checkpoint_good(PURCHASE_ID), "order": PURCHASE_ID})
    assert "Esperanto - French Dictionary" in response


@responses.activate()
def test_downloads_bilingual_purchase_dictionary_override(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    order = deepcopy(ORDER_P)
    order.dictionary = "eo-fr"
    order.dictionary_override = "eo-eo"
    utils.store_order(order)

    response = app.get("/download/eo/eo", params={"checkpoint": checkpoint_good(PURCHASE_ID), "order": PURCHASE_ID})
    assert "Esperanto Dictionary" in response
    assert (
        next(
            record.getMessage()
            for record in caplog.records
            if record.levelname == "INFO" and record.filename == "models.py"
        )
        == f"[order ID='{PURCHASE_ID}'] Dictionary override: 'eo-fr' -> 'eo-eo'"
    )


@responses.activate()
def test_downloads_bilingual_subscription(app: TestApp, mock_responses: Generator) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    response = app.get(
        "/download/eo/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
    )
    assert "Esperanto - French Dictionary" in response


@responses.activate()
def test_downloads_bilingual_subscription_dictionary_override(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    order.dictionary_override = "eo-eo"
    utils.store_order(order)

    for should_be_cached in [False, True]:
        response = app.get(
            "/download/eo/eo",
            params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        )
        assert "Esperanto Dictionary" in response
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers

    assert (
        next(
            record.getMessage()
            for record in caplog.records
            if record.levelname == "INFO" and record.filename == "models.py"
        )
        == f"[order ID='{SUBSCRIPTION_ID}'] Dictionary override: 'eo-fr' -> 'eo-eo'"
    )


@responses.activate()
def test_downloads_monolingual_unknown_dictionary(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/zz", status=404)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download monolingual] The dictionary zz-zz does not exist, or is disabled"
    )


def test_downloads_monolingual(app: TestApp) -> None:
    for should_be_cached in [False, True]:
        response = app.get("/download/eo")
        assert "Esperanto Dictionary" in response
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


def test_landing_page_bilingual_unknown_dictionary(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/get/eo/zz", status=404)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/get bilingual] The dictionary eo-zz does not exist, or is disabled"
    )


def test_landing_page_bilingual(app: TestApp) -> None:
    for should_be_cached in [False, True]:
        response = app.get("/get/eo/fr")
        assert "Esperanto - French Dictionary" in response
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


@responses.activate()
def test_file_download_bilingual_purchase(app: TestApp, mock_responses: Generator) -> None:
    order = deepcopy(ORDER_P)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    links = utils.craft_downloads_url(
        utils.load_dictionaries()["eo"]["fr"],
        order_type="purchase",
        order_id=PURCHASE_ID,
    )
    response = app.get(f"/file/{links['kobo'][3]}")
    assert response.headers["File-Source"] == "purchase"
    assert response.body == b"AwEsOmE DiCt!"


@responses.activate()
def test_file_download_bilingual_subscription(app: TestApp, mock_responses: Generator) -> None:
    order = deepcopy(ORDER_S)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    links = utils.craft_downloads_url(
        utils.load_dictionaries()["eo"]["fr"],
        order_type="subscription",
        order_id=SUBSCRIPTION_ID,
    )
    response = app.get(f"/file/{links['kobo'][3]}")
    assert response.headers["File-Source"] == "subscription"
    assert response.body == b"AwEsOmE DiCt!"


def test_file_download_bilingual_not_in_cache(app: TestApp) -> None:
    app.get("/file/uid", status=410)


def test_file_download_bilingual_inexistant(app: TestApp) -> None:
    links = utils.craft_downloads_url(utils.load_dictionaries()["eo"]["fr"])
    app.get(f"/file/{links['kobo'][4]}", status=404)


def test_file_download_monolingual(app: TestApp) -> None:
    response = app.get("/file/eo/dicthtml-eo-eo.zip")
    assert response.body == b"AwEsOmE DiCt!"


def test_file_download_monolingual_inexistant(app: TestApp) -> None:
    app.get("/file/fr/zz", status=404)


def test_file_download_monolingual_file_not_found(app: TestApp) -> None:
    app.get("/file/eo/dicthtml-eo-eo-noetym.zip", status=404)


def test_hall_of_fame(app: TestApp) -> None:
    app.get("/hall-of-fame")


def test_home(app: TestApp) -> None:
    for should_be_cached in [False, True]:
        response = app.get("/")
        assert f"<title>{constants.PROJECT}" in response
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


def test_list_all(app: TestApp) -> None:
    response = app.get("/list")
    assert "The Dictionaries List" in response


def test_sponsors(app: TestApp) -> None:
    response = app.get("/sponsors")
    assert "Diamond" in response
    assert "Gold" in response


def test_enjoy(app: TestApp) -> None:
    response = app.get("/enjoy")
    assert "You Are Awesome!" in response


def test_ads(app: TestApp) -> None:
    response = app.get("/ads.txt")
    content = response.body
    assert content.strip() == b"OWNERDOMAIN=reader-dict.com"


def test_humans(app: TestApp) -> None:
    response = app.get("/humans.txt")
    content = response.body
    assert b"/* TEAM */" in content
    assert b"/* SITE */" in content


def test_robots(app: TestApp) -> None:
    response = app.get("/robots.txt")
    content = response.body
    assert b"User-agent: *" in content
    assert b"Sitemap: " in content


def test_security(app: TestApp) -> None:
    response = app.get("/.well-known/security.txt")
    content = response.body
    assert b"Contact: " in content
    assert b"Acknowledgments: " in content


def test_sitemap(app: TestApp) -> None:
    response = app.get("/sitemap.xml")
    urls_count = response.body.count(b"<url>")
    assert urls_count > len(server.SUPPORTED_LOCALES) + 2


#
# Obsolete, to remove when relevant orders will be ended.
#

#
# Old URL (before 2025-09-09)
#


@responses.activate()
def test_download_monolingual_localized(app: TestApp) -> None:
    response = app.get("/en/file/eo/dicthtml-eo-eo.zip", status=302)
    assert response.headers["Location"].endswith("/file/eo/dicthtml-eo-eo.zip")


@responses.activate()
def test_download_bilingual_localized(app: TestApp) -> None:
    order = deepcopy(ORDER_P)
    order.dictionary = "eo-fr"
    utils.store_order(order)

    links = utils.craft_downloads_url(
        utils.load_dictionaries()["eo"]["fr"],
        order_type="purchase",
        order_id=PURCHASE_ID,
    )
    response = app.get(f"/en/file/{links['kobo'][3]}", status=302)
    assert response.headers["Location"].endswith(f"/file/{links['kobo'][3]}")


@responses.activate()
def test_downloads_monolingual_localized(app: TestApp) -> None:
    response = app.get("/en/download/eo", status=302)
    assert response.headers["Location"].endswith("/download/eo")


@responses.activate()
def test_downloads_bilingual_localized(app: TestApp) -> None:
    utils.store_order(ORDER_P)
    checkpoint = checkpoint_good(PURCHASE_ID)

    response = app.get("/en/download/eo/fr", params={"checkpoint": checkpoint, "order": PURCHASE_ID}, status=302)
    assert response.headers["Location"].endswith(f"/download/eo/fr?checkpoint={checkpoint}&order={PURCHASE_ID}")


@responses.activate()
def test_faq_localized(app: TestApp) -> None:
    response = app.get("/en/faq", status=302)
    assert response.headers["Location"].endswith("/")


@responses.activate()
def test_home_localized(app: TestApp) -> None:
    response = app.get("/en/", status=302)
    assert response.headers["Location"].endswith("/")


#
# Old URL (before 2025-05-16)
#


@responses.activate()
def test_downloads_bilingual_old(app: TestApp, mock_responses: Generator) -> None:
    """Old URL (before 2025-05-16)."""
    utils.store_order(ORDER_P)
    checkpoint = checkpoint_good(PURCHASE_ID)

    response = app.get(f"/en/download/eo/fr/{PURCHASE_ID}", params={"checkpoint": checkpoint}, status=302)
    assert response.headers["Location"].endswith(f"download/eo/fr?checkpoint={checkpoint}&order={PURCHASE_ID}")
