import json
from collections.abc import Generator
from copy import deepcopy
from unittest.mock import patch

import bottle
import bottle_file_cache
import pytest
import responses
from webtest import TestApp

from src import constants, paypal, server, utils

from .payloads import PAYPAL_CERT_URL, PURCHASE_ID, SUBSCRIPTION_DATA, SUBSCRIPTION_ID

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
        assert json.loads(response.body) == utils.load_dictionaries()
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


@responses.activate()
def test_api_order_purchase(app: TestApp, mock_responses: Generator) -> None:
    event = {"id": PURCHASE_ID, "payer": {}}
    response = app.post_json(constants.ROUTE_API_ORDER, event)
    assert '"status": "ok"' in response


@responses.activate()
def test_api_order_subscription(app: TestApp, mock_responses: Generator) -> None:
    event = {
        "orderID": "order-id",
        "subscriptionID": SUBSCRIPTION_ID,
        "facilitatorAccessToken": "some-token",
        "paymentSource": "paypal",
    }
    response = app.post_json(constants.ROUTE_API_ORDER, event)
    assert '"status": "ok"' in response


@responses.activate()
def test_api_webhook_paypal(app: TestApp, mock_responses: Generator) -> None:
    headers = {
        "Paypal-Transmission-Time": "2025-04-05T20:32:44Z",
        "Paypal-Cert-Url": PAYPAL_CERT_URL,
        "Paypal-Transmission-Sig": "Dss1lP9Y8D+ZXQ5VIbW/91wykhEpH06KUSEOmIGceJlSd33AE1nBT/UiNxz/i4/6EP31a7Sx44CjLOQtkJ+LYWK5aA4YkVu/e+CZ/nMLB1FW6lJXEflt0DGRusNaBDpq7WrfCHNiScquRMh3E4eUODfTSowvsiPf2UWkfbk0e/ELMky8YaFTS6gIhUdaRh1U8lUbv+IXi7v5pSGQOTtmrHR28fvPc+D8fSsl0tBfakpRPUNskNmRwJYYngQ0NzAO7cNAzCf3Es5yEAiJW9FgjawHmOkeoWSjWIXH7SKO7q1tqCRCE/+iu3jtK3q+wmq6iVq1luglzndgqNKTw+DwaQ==",  # noqa: E501
        "Paypal-Transmission-Id": "212a639d-125d-11f0-8798-c5d6de2737a0",
    }
    payload = json.dumps(
        {
            "id": "WH-1F78928319310462G-18R51787X87914712",
            "event_version": "1.0",
            "create_time": "2025-04-05T20:32:40.508Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.PENDING",
            "summary": "Payment pending for € 10.0 EUR",
            "resource": {
                "id": "10H81276XF6353701",
                "state": "completed",
                "amount": {"total": "10.00", "currency": "EUR", "details": {"subtotal": "10.00"}},
                "payment_mode": "INSTANT_TRANSFER",
                "protection_eligibility": "ELIGIBLE",
                "protection_eligibility_type": "ITEM_NOT_RECEIVED_ELIGIBLE,UNAUTHORIZED_PAYMENT_ELIGIBLE",
                "payment_hold_status": "HELD",
                "payment_hold_reasons": ["PAYMENT_HOLD"],
                "transaction_fee": {"value": "0.64", "currency": "EUR"},
                "invoice_number": "",
                "billing_agreement_id": "I-YSW93404E5CF",
                "create_time": "2025-04-05T20:32:35Z",
                "update_time": "2025-04-05T20:32:35Z",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/10H81276XF6353701",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/10H81276XF6353701/refund",
                        "rel": "refund",
                        "method": "POST",
                    },
                ],
                "soft_descriptor": "PAYPAL *READERDICT",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-1F78928319310462G-18R51787X87914712",
                    "rel": "self",
                    "method": "GET",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-1F78928319310462G-18R51787X87914712/resend",
                    "rel": "resend",
                    "method": "POST",
                },
            ],
        },
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()

    with patch.object(constants, "PAYPAL_WEBHOOK_ID", "40L71081MK3756722"):
        app.post(constants.ROUTE_API_WEBHOOK_PAYPAL, payload, headers=headers, status=500, expect_errors=True)


@responses.activate()
def test_api_webhook_paypal_verification_error(
    caplog: pytest.LogCaptureFixture, app: TestApp, mock_responses: Generator
) -> None:
    headers = {
        "Paypal-Transmission-Time": "2025-04-05T20:32:44Z",
        "Paypal-Cert-Url": PAYPAL_CERT_URL,
        "Paypal-Transmission-Sig": "Dss1lP9Y8D+ZXQ5VIbW/91wykhEpH06KUSEOmIGceJlSd33AE1nBT/UiNxz/i4/6EP31a7Sx44CjLOQtkJ+LYWK5aA4YkVu/e+CZ/nMLB1FW6lJXEflt0DGRusNaBDpq7WrfCHNiScquRMh3E4eUODfTSowvsiPf2UWkfbk0e/ELMky8YaFTS6gIhUdaRh1U8lUbv+IXi7v5pSGQOTtmrHR28fvPc+D8fSsl0tBfakpRPUNskNmRwJYYngQ0NzAO7cNAzCf3Es5yEAiJW9FgjawHmOkeoWSjWIXH7SKO7q1tqCRCE/+iu3jtK3q+wmq6iVq1luglzndgqNKTw+DwaQ==",  # noqa: E501
        "Paypal-Transmission-Id": "212a639d-125d-11f0-8798-c5d6de2737a0",
    }
    payload = json.dumps(
        {
            "id": "WH-1F78928319310462G-18R51787X87914712",
            "event_version": "1.0",
            "create_time": "2025-04-05T20:32:40.508Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.PENDING",
            "summary": "Payment pending for € 10.0 EUR",
        },
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()

    response = app.post(constants.ROUTE_API_WEBHOOK_PAYPAL, payload, headers=headers)
    assert response.status_code == 200

    assert [record.getMessage().split("\n", 1)[0] for record in caplog.records if record.levelname == "ERROR"] == [
        "PayPal webhook signature failed",
    ]


@pytest.mark.parametrize(
    ("kind", "file"),
    [
        ("font", "Lora-Regular.woff2"),
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
    ],
)
def test_custom_error(status: str) -> None:
    error = bottle.HTTPError(status)
    assert "I am sorry" in server.custom_error(error)


@responses.activate()
def test_downloads_bilingual_no_order_id(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details"
    )


@responses.activate()
def test_downloads_bilingual_no_checkpoint(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", params={"order": "uid"}, status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details"
    )


@responses.activate()
def test_downloads_bilingual_invalid_checkpoint(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    app.get("/download/eo/fr", params={"checkpoint": "bad", "order": "uid"}, status=400)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == "[/download bilingual] Missing mandatory details"
    )


@responses.activate()
def test_downloads_bilingual_unknown_dictionary(
    app: TestApp, caplog: pytest.LogCaptureFixture, mock_responses: Generator
) -> None:
    assert '"status": "ok"' in paypal.register_order("subscription", SUBSCRIPTION_ID)
    app.get(
        "/download/zz/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=404,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] The dictionary zz-fr does not exist, or is disabled"
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
    paypal.register_order("subscription", SUBSCRIPTION_ID)
    app.get("/download/eo/fr", params={"checkpoint": CHECKPOINT_BAD, "order": SUBSCRIPTION_ID}, status=403)
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] Checkpoint '{CHECKPOINT_BAD}' is invalid"
    )


@responses.activate()
def test_downloads_bilingual_subscription_status_not_ok(app: TestApp, caplog: pytest.LogCaptureFixture) -> None:
    data = deepcopy(SUBSCRIPTION_DATA)
    data["status"] = "CANCELLED"

    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=data)

    paypal.register_order("subscription", SUBSCRIPTION_ID)
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
    paypal.register_order("subscription", SUBSCRIPTION_ID)
    app.get(
        "/download/all/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=404,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] The dictionary all-fr does not exist, or is disabled"
    )


@responses.activate()
def test_downloads_bilingual_dictionaries_mismatch(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    paypal.register_order("subscription", SUBSCRIPTION_ID)
    app.get(
        "/download/eo/eo",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        status=403,
    )
    assert (
        next(record.getMessage() for record in caplog.records if record.levelname == "ERROR")
        == f"[/download order ID='{SUBSCRIPTION_ID}'] Dictionary mismatch: requested='eo-eo', available='eo-fr'"
    )


@responses.activate()
def test_downloads_bilingual_purchase_dictionary(app: TestApp, mock_responses: Generator) -> None:
    paypal.register_order("purchase", PURCHASE_ID)
    response = app.get("/download/eo/fr", params={"checkpoint": checkpoint_good(PURCHASE_ID), "order": PURCHASE_ID})
    assert "here are your files" in response


@responses.activate()
def test_downloads_bilingual_purchase_dictionary_override(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    paypal.register_order("purchase", PURCHASE_ID)

    order = utils.get_order(PURCHASE_ID)
    assert order
    order.dictionary_override = "eo-eo"
    utils.store_order(order)

    response = app.get("/download/eo/eo", params={"checkpoint": checkpoint_good(PURCHASE_ID), "order": PURCHASE_ID})
    assert "here are your files" in response
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
    paypal.register_order("subscription", SUBSCRIPTION_ID)
    response = app.get(
        "/download/eo/fr",
        params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
    )
    assert "here are your files" in response


@responses.activate()
def test_downloads_bilingual_subscription_dictionary_override(
    app: TestApp,
    caplog: pytest.LogCaptureFixture,
    mock_responses: Generator,
) -> None:
    paypal.register_order("subscription", SUBSCRIPTION_ID)

    order = utils.get_order(SUBSCRIPTION_ID)
    assert order
    order.dictionary_override = "eo-eo"
    utils.store_order(order)

    for should_be_cached in [False, True]:
        response = app.get(
            "/download/eo/eo",
            params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID), "order": SUBSCRIPTION_ID},
        )
        assert "here are your files" in response
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
def test_downloads_bilingual_old(app: TestApp, mock_responses: Generator) -> None:
    paypal.register_order("subscription", SUBSCRIPTION_ID)
    response = app.get(f"/en/download/eo/fr/{SUBSCRIPTION_ID}", params={"checkpoint": checkpoint_good(SUBSCRIPTION_ID)})
    assert "here are your files" in response


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
        assert "here are your files" in response
        if should_be_cached:
            assert bottle_file_cache.CONFIG.header_name in response.headers
        else:
            assert bottle_file_cache.CONFIG.header_name not in response.headers


@responses.activate()
def test_file_download_bilingual_purchase(app: TestApp, mock_responses: Generator) -> None:
    paypal.register_order("purchase", PURCHASE_ID)
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
    paypal.register_order("subscription", SUBSCRIPTION_ID)
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
    assert urls_count == 15
