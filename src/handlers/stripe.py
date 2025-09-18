import hmac
import logging
from contextlib import suppress
from datetime import UTC, datetime
from hashlib import sha256

import requests
import ulid

from src import constants, utils
from src.handlers import base
from src.models import Order

log = logging.getLogger(__name__)
SESSION = requests.Session()

SESSION.headers.update(constants.HTTP_HEADERS)
SESSION.headers["Authorization"] = f"Bearer {constants.STRIPE_API_KEY}"


def is_valid_client_id(value: str) -> bool:
    with suppress(Exception):
        ulid.ULID.from_str(value)
        return True
    return False


def is_valid_dictionary(value: str) -> bool:
    return bool(utils.get_dictionary_from_key("name", value))


def extract_client_info(data: dict) -> tuple[str, str]:
    """`client_reference_id` contains `ULID-LANG_SRC-LANG_DST`. Check the data syntax, and legitimity."""
    if (reference := data.get("client_reference_id") or "").count("-") == 2:
        client_id, dictionary = reference.split("-", 1)
        if is_valid_client_id(client_id) and is_valid_dictionary(dictionary):
            return client_id, dictionary

    msg = f"[stripe, order ID={data['payment_intent']!r}] client_reference_id malformed: {reference!r}"
    raise ValueError(msg)


def purchase_status(data: dict) -> str:
    return (
        "completed"
        if (data["mode"] == "payment" and data["payment_status"] == "paid" and data["status"] == "complete")
        else "failed"
    )


class Handler(base.Handler):
    source = "stripe"

    def create_checkout_session_url(self, lang_src: str, lang_dst: str) -> dict[str, str]:
        dictionary = f"{lang_src}-{lang_dst}"
        client_reference_id = f"{ulid.ULID()}-{dictionary}"
        data = "&".join(
            [
                "mode=payment",
                f"success_url=https://www.{constants.WWW}/enjoy",
                f"cancel_url=https://www.{constants.WWW}/#{dictionary}",
                f"client_reference_id={client_reference_id}",
                f"line_items[0][price]={constants.STRIPE_PRICE_ID}",
                "line_items[0][quantity]=1",
                "custom_fields[0][key]=dictionary",
                "custom_fields[0][label][type]=custom",
                f"custom_fields[0][label][custom]={constants.PROJECT}",
                "custom_fields[0][type]=text",
                f"custom_fields[0][text][default_value]={dictionary}",
            ]
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        with SESSION.post(constants.STRIPE_URL_CHECKOUT_SESSION, headers=headers, data=data, timeout=30) as req:
            data = req.json()
            req.raise_for_status()
            return data

    def is_valid_webhook_event(self, headers: dict[str, str], payload: bytes) -> bool:
        header = headers["Stripe-Signature"]
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = int(next(i[1] for i in list_items if i[0] == "t"))
        signatures = [i[1] for i in list_items if i[0] == "v1"]
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_sig = hmac.new(constants.STRIPE_WEBHOOK_SEC_KEY.encode(), signed_payload.encode(), sha256).hexdigest()
        return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)

    def handle_webhook(self, event: dict) -> dict[str, str]:
        data = event["data"]["object"]
        order_id = data["payment_intent"]

        match event["type"]:
            case constants.STRIPE_EVENT_PURCHASE_COMPLETED:
                checkout_session_id = data["id"]
                return self.register_order(order_id, checkout_session_id)

            case constants.STRIPE_EVENT_PURCHASE_REFUNDED:
                if not (order := utils.get_order(order_id)):
                    return {"status": "error", "message": "no such purchase"}

                if not (data["refunded"] and data["captured"] and data["paid"] and order.status != "refunded"):
                    return {"status": "info", "message": "purchase unchanged"}

                order.status = "refunded"
                order.status_update_time = datetime.fromtimestamp(data["created"], UTC).isoformat()
                utils.store_order(order)
                return {"status": "ok", "message": "purchase status updated"}

        return {"status": "info", "message": "event not interesting"}

    def _fetch_order_impl(self, kind: str, order_id: str) -> Order:  # noqa: ARG002
        """Note: `order_id` is actually the checkout session ID."""
        url = f"{constants.STRIPE_URL_CHECKOUT_SESSION}/{order_id}"
        with SESSION.get(url, timeout=30) as req:
            req.raise_for_status()
            data = req.json()

        client_id, dictionary = extract_client_info(data)
        return Order(
            data["payment_intent"],
            dictionary=dictionary,
            email=data["customer_email"] or data.get("customer_details", {}).get("email", ""),
            source=self.source,
            status=purchase_status(data),
            status_update_time=datetime.fromtimestamp(data["created"], UTC).isoformat(),
            ulid=client_id,
            user=data.get("customer_details", {}).get("name", "").split(" ", 1)[0],
        )
