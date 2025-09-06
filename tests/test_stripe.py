from collections.abc import Generator
from copy import deepcopy
from unittest.mock import patch

import responses

from src import constants, handlers, utils
from src.models import Order

from .payloads import (
    STRIPE_CHECKOUT_SESSION_DATA,
    STRIPE_PURCHASE_ID,
    STRIPE_REFUND_DATA,
    STRIPE_WEBHOOK_HEADERS,
    STRIPE_WEBHOOK_PAYLOAD,
    STRIPE_WEBHOOK_SEC_KEY,
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


def test_is_valid_webhook_event() -> None:
    handler = handlers.get("stripe")
    with patch.object(constants, "STRIPE_WEBHOOK_SEC_KEY", STRIPE_WEBHOOK_SEC_KEY):
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
