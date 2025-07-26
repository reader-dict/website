from collections.abc import Generator
from copy import deepcopy

import pytest
import responses
from freezegun import freeze_time
from responses.registries import OrderedRegistry

from src import cache, constants, handlers, utils
from src.handlers import paypal

from .payloads import (
    ORDER_P,
    ORDER_S,
    PAYPAL_CERT,
    PAYPAL_CERT_URL,
    PAYPAL_WEBHOOK_HEADERS,
    PAYPAL_WEBHOOK_PAYLOAD,
    PURCHASE_ID,
    STATUS_UPDATE_TIME,
    SUBSCRIPTION_DATA,
    SUBSCRIPTION_ID,
)


@responses.activate()
def test_fetch_order_purchase(mock_responses: Generator) -> None:
    assert handlers.get("paypal").fetch_order("purchase", PURCHASE_ID) == ORDER_P


@freeze_time(STATUS_UPDATE_TIME)
@responses.activate()
def test_fetch_order_subscription(mock_responses: Generator) -> None:
    assert handlers.get("paypal").fetch_order("subscription", SUBSCRIPTION_ID) == ORDER_S


@responses.activate()
def test_fetch_order_subscription_without_email_address() -> None:
    data = deepcopy(SUBSCRIPTION_DATA)
    data["subscriber"].pop("email_address")  # type: ignore[attr-defined]

    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=data)

    assert not handlers.get("paypal").fetch_order("subscription", SUBSCRIPTION_ID).email


@responses.activate(registry=OrderedRegistry)
def test_fetch_order_subscription_expired_access_token() -> None:
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), status=401)
    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "renewed"})
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(SUBSCRIPTION_ID), json=SUBSCRIPTION_DATA)

    cache.add_notimer(paypal.TOKEN_CACHE_KEY, "expired")
    assert handlers.get("paypal").fetch_order("subscription", SUBSCRIPTION_ID) == ORDER_S
    assert cache.get_notimer(paypal.TOKEN_CACHE_KEY) == "renewed"


@responses.activate()
def test_get_access_token_found_in_cache() -> None:
    cache.add_notimer(paypal.TOKEN_CACHE_KEY, "secured")
    assert paypal.get_access_token() == "secured"


@responses.activate()
def test_get_certificate(mock_responses: Generator) -> None:
    assert paypal.get_certificate(PAYPAL_CERT_URL) == PAYPAL_CERT
    assert cache.get_notimer(PAYPAL_CERT_URL) == PAYPAL_CERT


@responses.activate()
def test_get_certificate_found_in_cache() -> None:
    cache.add_notimer(PAYPAL_CERT_URL, PAYPAL_CERT)
    assert paypal.get_certificate(PAYPAL_CERT_URL) == PAYPAL_CERT


@responses.activate()
def test_is_valid_webhook_event(mock_responses: Generator) -> None:
    assert handlers.get("paypal").is_valid_webhook_event(PAYPAL_WEBHOOK_HEADERS, PAYPAL_WEBHOOK_PAYLOAD)

    assert not handlers.get("paypal").is_valid_webhook_event(
        PAYPAL_WEBHOOK_HEADERS, PAYPAL_WEBHOOK_PAYLOAD + b"more data"
    )


@freeze_time(STATUS_UPDATE_TIME)
@responses.activate()
def test_handle_webhook_purchase_refunded(mock_responses: Generator) -> None:
    utils.store_order(ORDER_P)

    event = {"event_type": constants.PAYPAL_EVENT_PURCHASE_REFUNDED, "resource": {"invoice_id": "capture-id"}}
    updated = deepcopy(ORDER_P)
    updated.status = "refunded"
    updated.status_update_time = STATUS_UPDATE_TIME
    handler = handlers.get("paypal")
    assert '"status": "ok"' in handler.handle_webhook(event)

    assert utils.load_orders() == {PURCHASE_ID: updated}

    # Idempotency
    assert "purchase unchanged" in handler.handle_webhook(event)
    assert utils.load_orders() == {PURCHASE_ID: updated}


def test_handle_webhook_purchase_refunded_no_such_order() -> None:
    event = {"event_type": constants.PAYPAL_EVENT_PURCHASE_REFUNDED, "resource": {"invoice_id": "capture-id"}}
    handler = handlers.get("paypal")
    assert "no such purchase" in handler.handle_webhook(event)


@responses.activate()
def test_handle_webhook_subscription_cancelled(mock_responses: Generator) -> None:
    utils.store_order(ORDER_S)

    event = {
        "event_type": constants.PAYPAL_EVENT_SUBSCRIPTION_CANCELLED,
        "resource": {"id": SUBSCRIPTION_ID, "status": "CANCELLED", "status_update_time": "cancelled_time"},
    }
    updated = deepcopy(ORDER_S)
    updated.status = "cancelled"
    updated.status_update_time = "cancelled_time"
    handler = handlers.get("paypal")
    assert '"status": "ok"' in handler.handle_webhook(event)

    assert utils.load_orders() == {SUBSCRIPTION_ID: updated}

    # Idempotency
    assert "subscription unchanged" in handler.handle_webhook(event)
    assert utils.load_orders() == {SUBSCRIPTION_ID: updated}


@responses.activate()
def test_handle_webhook_subscription_cancelled_no_such_order(mock_responses: Generator) -> None:
    event = {
        "event_type": constants.PAYPAL_EVENT_SUBSCRIPTION_CANCELLED,
        "resource": {"id": SUBSCRIPTION_ID, "status": "CANCELLED", "status_update_time": "cancelled_time"},
    }
    handler = handlers.get("paypal")
    assert "no such subscription" in handler.handle_webhook(event)


@responses.activate()
def test_handle_webhook_subscription_suspended(mock_responses: Generator) -> None:
    utils.store_order(ORDER_S)

    event = {
        "event_type": constants.PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED,
        "resource": {"id": SUBSCRIPTION_ID, "update_time": "suspended_time"},
    }
    updated = deepcopy(ORDER_S)
    updated.status = "suspended"
    updated.status_update_time = "suspended_time"
    handler = handlers.get("paypal")
    assert '"status": "ok"' in handler.handle_webhook(event)

    assert utils.load_orders() == {SUBSCRIPTION_ID: updated}

    # Idempotency
    assert "subscription unchanged" in handler.handle_webhook(event)
    assert utils.load_orders() == {SUBSCRIPTION_ID: updated}


@responses.activate()
def test_handle_webhook_subscription_suspended_no_such_order(mock_responses: Generator) -> None:
    event = {
        "event_type": constants.PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED,
        "resource": {"id": SUBSCRIPTION_ID, "update_time": "suspended_time"},
    }
    handler = handlers.get("paypal")
    assert "no such subscription" in handler.handle_webhook(event)


@responses.activate()
def test_handle_webhook_uninteresting() -> None:
    event = {"event_type": "foo"}
    handler = handlers.get("paypal")
    assert "event not interesting" in handler.handle_webhook(event)


@pytest.mark.parametrize("status", ["COMPLETED", "REFUNDED"])
def test_purchase_completed(status: str) -> None:
    data = {
        "id": "id",
        "status": "COMPLETED",
        "purchase_units": [{"payments": {"captures": [{"status": status}]}}],
    }
    assert paypal.purchase_status(data) == status.lower()
