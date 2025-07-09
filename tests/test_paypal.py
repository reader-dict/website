import json
from collections.abc import Generator
from copy import deepcopy
from unittest.mock import patch

import pytest
import responses
import ulid
from freezegun import freeze_time
from responses.registries import OrderedRegistry

from src import cache, constants, models, paypal, utils

from .payloads import (
    PAYPAL_CERT,
    PAYPAL_CERT_URL,
    PLAN_ID,
    PURCHASE_DATA,
    PURCHASE_ID,
    STATUS_UPDATE_TIME,
    SUBSCRIPTION_DATA,
    SUBSCRIPTION_ID,
)

ORDER_P = models.Order(
    PURCHASE_ID,
    dictionary="eo-fr",
    email="alice@example.org",
    invoice_id="capture-id",
    status="completed",
    status_update_time=STATUS_UPDATE_TIME,
    ulid="01JVRQ7C9RTEHHFPY30RDQYZPR",
    user="Alice",
)
ORDER_S = models.Order(
    SUBSCRIPTION_ID,
    email="alice@example.org",
    plan_id=PLAN_ID,
    status="active",
    status_update_time=STATUS_UPDATE_TIME,
    ulid="01JVRQ7C9RTEHHFPY30RDQYZPR",
    user="Alice",
)


@responses.activate()
def test_fetch_order_purchase(mock_responses: Generator) -> None:
    assert paypal.fetch_order("purchase", PURCHASE_ID) == ORDER_P


@freeze_time(STATUS_UPDATE_TIME)
@responses.activate()
def test_fetch_order_subscription(mock_responses: Generator) -> None:
    assert paypal.fetch_order("subscription", SUBSCRIPTION_ID) == ORDER_S


@responses.activate()
def test_fetch_order_subscription_without_email_address() -> None:
    data = deepcopy(SUBSCRIPTION_DATA)
    data["subscriber"].pop("email_address")  # type: ignore[attr-defined]

    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=data)

    assert not paypal.fetch_order("subscription", SUBSCRIPTION_ID).email


@responses.activate(registry=OrderedRegistry)
def test_fetch_order_subscription_expired_access_token() -> None:
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), status=401)
    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "renewed"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=SUBSCRIPTION_DATA)

    cache.add_notimer("access-token", "expired")
    assert paypal.fetch_order("subscription", SUBSCRIPTION_ID) == ORDER_S
    assert cache.get_notimer("access-token") == "renewed"


@responses.activate()
def test_get_access_token_found_in_cache() -> None:
    cache.add_notimer("access-token", "secured")
    assert paypal.get_access_token() == "secured"


@responses.activate()
def test_get_certificate(mock_responses: Generator) -> None:
    assert paypal.get_certificate(PAYPAL_CERT_URL) == PAYPAL_CERT
    assert cache.get_notimer(PAYPAL_CERT_URL) == PAYPAL_CERT


@responses.activate()
def test_get_certificate_found_in_cache() -> None:
    cache.add_notimer(PAYPAL_CERT_URL, PAYPAL_CERT)
    assert paypal.get_certificate(PAYPAL_CERT_URL) == PAYPAL_CERT


@freeze_time(STATUS_UPDATE_TIME)
@responses.activate()
def test_handle_webhook_purchase(mock_responses: Generator) -> None:
    order_id = PURCHASE_ID
    event_completed = {
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {"supplementary_data": {"related_ids": {"order_id": order_id}}},
    }
    event_refunded = {
        "event_type": "PAYMENT.CAPTURE.REFUNDED",
        "resource": {"invoice_id": "capture-id"},
    }

    #
    # Purchase completed
    #

    with patch.object(models, "make_ulid", return_value=ORDER_P.ulid):
        assert '"status": "ok"' in paypal.handle_webhook(event_completed)
    assert '"status": "info"' in paypal.handle_webhook(event_completed)

    expected = models.Order(**ORDER_P.as_dict() | {"dictionary": "eo-fr", "source": "paypal"})
    assert utils.load_orders() == {order_id: expected}

    # Check the email sent
    assert (constants.EMAILS / f"{order_id}.msg").is_file()

    #
    # Purchase refunded
    #

    assert '"status": "ok"' in paypal.handle_webhook(event_refunded)
    assert '"status": "info"' in paypal.handle_webhook(event_refunded)
    expected.status = "refunded"
    assert utils.load_orders() == {order_id: expected}


@responses.activate()
def test_handle_webhook_subscription(mock_responses: Generator) -> None:
    order_id = SUBSCRIPTION_ID
    event_completed = {"event_type": "PAYMENT.SALE.COMPLETED", "resource": {"billing_agreement_id": order_id}}
    event_cancelled = {
        "event_type": "BILLING.SUBSCRIPTION.CANCELLED",
        "resource": {"id": order_id, "status": "CANCELLED", "status_update_time": "cancelled_time"},
    }
    event_suspended = {
        "event_type": "BILLING.SUBSCRIPTION.SUSPENDED",
        "resource": {"id": order_id, "update_time": "suspended_time"},
    }

    #
    # Subscription completed
    #

    with patch.object(models, "make_ulid", return_value=ORDER_S.ulid):
        assert '{"status": "ok", "url":' in paypal.handle_webhook(event_completed)
    assert paypal.handle_webhook(event_completed) == '{"status": "info", "message": "subscription ID already exists"}'

    expected = models.Order(**ORDER_S.as_dict() | {"dictionary": "eo-fr", "source": "paypal"})
    assert utils.load_orders() == {order_id: expected}

    # Check the email sent
    assert (constants.EMAILS / f"{order_id}.msg").is_file()

    #
    # Subscription suspended
    #

    assert paypal.handle_webhook(event_suspended) == '{"status": "ok", "message": "subscription status updated"}'
    assert paypal.handle_webhook(event_suspended) == '{"status": "info", "message": "subscription unchanged"}'
    expected.status = "suspended"
    expected.status_update_time = "suspended_time"
    assert utils.load_orders() == {order_id: expected}

    #
    # Subscription cancelled
    #

    assert paypal.handle_webhook(event_cancelled) == '{"status": "ok", "message": "subscription status updated"}'
    assert paypal.handle_webhook(event_cancelled) == '{"status": "info", "message": "subscription unchanged"}'
    expected.status = "cancelled"
    expected.status_update_time = "cancelled_time"
    assert utils.load_orders() == {order_id: expected}


@responses.activate()
def test_handle_webhook_not_interesting_event(mock_responses: Generator) -> None:
    order_id = SUBSCRIPTION_ID
    event = {"event_type": "BILLING.SUBSCRIPTION.CREATED", "resource": {"billing_agreement_id": order_id}}

    assert paypal.handle_webhook(event) == '{"status": "info", "message": "event not interesting"}'


@responses.activate()
def test_handle_webhook_unhandled_event(mock_responses: Generator) -> None:
    order_id = SUBSCRIPTION_ID
    event = {"event_type": "BILLING.SUBSCRIPTION.BOOMED", "resource": {"billing_agreement_id": order_id}}

    with pytest.raises(ValueError, match="Unhandled PayPal webhook"):
        paypal.handle_webhook(event)

    assert not utils.load_orders()


@responses.activate()
def test_is_valid_webhook_event(mock_responses: Generator) -> None:
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
        assert paypal.is_valid_webhook_event(headers, payload)
        assert not paypal.is_valid_webhook_event(headers, payload + b"more data")


def test_purchase_completed() -> None:
    data = {
        "id": "id",
        "status": "COMPLETED",
        "purchase_units": [{"payments": {"captures": [{"status": "COMPLETED"}]}}],
    }
    assert paypal.purchase_status(data)


def test_purchase_completed_falsy_refunded() -> None:
    data = {"id": "id", "status": "COMPLETED", "purchase_units": [{"payments": {"captures": [{"status": "REFUNDED"}]}}]}
    assert paypal.purchase_status(data) == "refunded"


@responses.activate()
@freeze_time("2025-05-21T22:01:30.780681+00:00")
@pytest.mark.parametrize(
    ("kind", "order_id"),
    [
        ("purchase", PURCHASE_ID),
        ("subscription", SUBSCRIPTION_ID),
    ],
)
def test_register_order(kind: str, order_id: str, mock_responses: Generator) -> None:
    assert not utils.load_orders()

    with patch.object(models, "make_ulid", return_value=(ORDER_P if kind == "purchase" else ORDER_S).ulid):
        assert '"status": "ok"' in paypal.register_order(kind, order_id)

    expected = models.Order(
        **(ORDER_P if kind == "purchase" else ORDER_S).as_dict() | {"dictionary": "eo-fr", "source": "paypal"}
    )
    if kind == "purchase":
        expected.dictionary = "eo-fr"
    else:
        expected.plan_id = "P-8TK09370UE116905RM7X56CQ"
    assert utils.load_orders() == {order_id: expected}

    # Check the email sent
    assert (constants.EMAILS / f"{order_id}.msg").is_file()

    if kind == "purchase":
        folder = constants.PURCHASE_FILES / PURCHASE_ID
        assert folder.is_dir()
        assert (folder / "dicthtml-eo-fr.zip").is_file()
        assert json.loads((folder / "metadata.json").read_text()) == {
            "buy-date": "2025-05-21T22:01:30.780681+00:00",
            "enabled": True,
            "formats": "df,dictorg,kobo,mobi,stardict",
            "plan_id": PLAN_ID,
            "progress": "format:mobi;templates:2/42",
            "uid": "01JR0WGRVP18RTFN6K57W42ZAX",
            "updated": "2025-04-04",
            "words": 151150,
        }


@responses.activate()
@pytest.mark.parametrize(
    ("kind", "order_id"),
    [
        ("purchase", PURCHASE_ID),
        ("subscription", SUBSCRIPTION_ID),
    ],
)
def test_register_order_already_existant(
    kind: str, order_id: str, caplog: pytest.LogCaptureFixture, mock_responses: Generator
) -> None:
    assert '"status": "ok"' in paypal.register_order(kind, order_id)
    assert '"status": "info"' in paypal.register_order(kind, order_id)
    assert [record.getMessage() for record in caplog.records if record.levelname == "INFO"][
        -1
    ] == f"Rejected {kind}, order ID '{order_id}' already exists"


@responses.activate()
def test_register_order_purchase_invalid_sku() -> None:
    data = deepcopy(PURCHASE_DATA)
    data["purchase_units"][0]["items"][0]["sku"] = "all-fr"  # type: ignore[index]

    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(constants.PAYPAL_URL_PURCHASES.format(PURCHASE_ID), json=data)

    assert not utils.load_orders()
    assert '"status": "error"' in paypal.register_order("purchase", PURCHASE_ID)
    assert not utils.load_orders()


@responses.activate()
def test_register_order_subscription_invalid_plan_id() -> None:
    data = deepcopy(SUBSCRIPTION_DATA)
    data["plan_id"] = "unknown"

    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=data)

    assert not utils.load_orders()
    assert '"status": "error"' in paypal.register_order("subscription", SUBSCRIPTION_ID)
    assert not utils.load_orders()


@responses.activate()
def test_create_plan(mock_responses: Generator) -> None:
    plan_id = "new-plan-id"
    uid = ulid.ULID()

    with patch.object(ulid, "ULID", return_value=uid):
        assert paypal.create_plan("fr", "fr", 9.49) == (plan_id, str(uid))
