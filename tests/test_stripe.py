from collections.abc import Generator
from copy import deepcopy

import pytest
import responses

from src import constants, handlers, utils
from src.handlers import stripe
from src.models import Order

from .payloads import (
    STRIPE_CHECKOUT_SESSION_DATA,
    STRIPE_CHECKOUT_SESSION_ID,
    STRIPE_PURCHASE_ID,
    STRIPE_REFUND_DATA,
    STRIPE_WEBHOOK_HEADERS,
    STRIPE_WEBHOOK_PAYLOAD,
)

ORDER = Order(
    id=STRIPE_PURCHASE_ID,
    dictionary="eo-fr",
    dictionary_override="",
    email="alice@example.org",
    invoice_id="",
    locale="en",
    plan_id="",
    source="stripe",
    status="completed",
    status_update_time="2025-09-05T14:01:28+00:00",
    ulid="01K4D2WZR8G1TG36RNF3020124",
    user="Alice",
)


def test_extract_client_info() -> None:
    client_reference_id = f"{ORDER.ulid}-{ORDER.dictionary}"
    expected = (ORDER.ulid, ORDER.dictionary)
    assert stripe.extract_client_info({"client_reference_id": client_reference_id}) == expected


@pytest.mark.parametrize(
    "client_reference_id",
    [
        # Invalid
        "",
        "-",
        "foo\nbar",
        # Invalid client ID
        "ulid-eo-fr",
        # Invalid dictionary
        f"{ORDER.ulid}-eo",
        f"{ORDER.ulid}-eo-",
        f"{ORDER.ulid}-eo-unknown",
        f"{ORDER.ulid}-eo-fr-",
        f"{ORDER.ulid}-eo-fr-foo",
    ],
)
def test_extract_client_info_falsy(client_reference_id: str) -> None:
    with pytest.raises(ValueError, match=".*client_reference_id malformed.*"):
        stripe.extract_client_info({"client_reference_id": client_reference_id, "payment_intent": "pi"})


def test_is_valid_client_id() -> None:
    assert stripe.is_valid_client_id(ORDER.ulid)


def test_is_valid_client_id_falsy() -> None:
    assert not stripe.is_valid_client_id(len(ORDER.ulid) * "9")


def test_is_valid_dictionary() -> None:
    assert stripe.is_valid_dictionary(ORDER.dictionary)


@pytest.mark.parametrize("value", ["fr-", "-fr", "unknown-fr", "fr-unknown"])
def test_is_valid_dictionary_falsy(value: str) -> None:
    assert not stripe.is_valid_dictionary(value)


def test_is_valid_webhook_event() -> None:
    handler = handlers.get("stripe")
    assert handler.is_valid_webhook_event(STRIPE_WEBHOOK_HEADERS, STRIPE_WEBHOOK_PAYLOAD)

    assert not handler.is_valid_webhook_event(STRIPE_WEBHOOK_HEADERS, STRIPE_WEBHOOK_PAYLOAD + b"more data")


@responses.activate()
def test_handle_webhook_purchase_completed(mock_responses: Generator) -> None:
    assert not utils.load_orders()

    event = {"data": {"object": STRIPE_CHECKOUT_SESSION_DATA}, "type": constants.STRIPE_EVENT_PURCHASE_COMPLETED}
    handler = handlers.get("stripe")
    assert '"status": "ok"' in handler.handle_webhook(event)

    assert utils.load_orders() == {STRIPE_PURCHASE_ID: ORDER}

    # Idempotency
    assert "purchase ID already exists" in handler.handle_webhook(event)
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: ORDER}


def test_handle_webhook_purchase_refunded() -> None:
    utils.store_order(ORDER)
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: ORDER}

    event = {"data": {"object": STRIPE_REFUND_DATA}, "type": constants.STRIPE_EVENT_PURCHASE_REFUNDED}
    handler = handlers.get("stripe")
    assert '"status": "ok"' in handler.handle_webhook(event)

    updated = deepcopy(ORDER)
    updated.status = "refunded"
    updated.status_update_time = "2025-09-05T14:01:43+00:00"
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: updated}

    # Idempotency
    assert "purchase unchanged" in handler.handle_webhook(event)
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: updated}


def test_handle_webhook_purchase_refunded_no_such_order() -> None:
    event = {"data": {"object": STRIPE_REFUND_DATA}, "type": constants.STRIPE_EVENT_PURCHASE_REFUNDED}
    handler = handlers.get("stripe")
    assert "no such purchase" in handler.handle_webhook(event)


@responses.activate()
def test_register_order_ids_mismatch(mock_responses: Generator) -> None:
    utils.store_order(ORDER)
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: ORDER}

    handler = handlers.get("stripe")
    ret = handler.register_order("falsified-id", STRIPE_CHECKOUT_SESSION_ID)
    assert "order ID mismatch" in ret

    utils.store_order(ORDER)
    assert utils.load_orders() == {STRIPE_PURCHASE_ID: ORDER}


@responses.activate()
def test_handle_webhook_uninteresting() -> None:
    event = {"data": {"object": STRIPE_REFUND_DATA}, "type": "foo"}
    handler = handlers.get("stripe")
    assert "event not interesting" in handler.handle_webhook(event)
