import hmac
import json
import logging
from contextlib import suppress
from datetime import UTC, datetime
from hashlib import sha256

import requests

from src import constants, utils
from src.handlers import base
from src.models import Order

log = logging.getLogger(__name__)
SESSION = requests.Session()
TOKEN_CACHE_KEY = "stripe-access-token"  # noqa: S105

SESSION.headers.update(constants.HTTP_HEADERS)
SESSION.headers["Authorization"] = f"Bearer {constants.STRIPE_API_KEY}"


def purchase_status(data: dict) -> str:
    return (
        "completed"
        if (data["mode"] == "payment" and data["payment_status"] == "paid" and data["status"] == "complete")
        else "failed"
    )


class Handler(base.Handler):
    source = "stripe"

    def is_valid_webhook_event(self, headers: dict[str, str], payload: bytes) -> bool:
        header = headers["Stripe-Signature"]
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = int(next(i[1] for i in list_items if i[0] == "t"))
        signatures = [i[1] for i in list_items if i[0] == "v1"]
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_sig = hmac.new(constants.STRIPE_WEBHOOK_SEC_KEY.encode(), signed_payload.encode(), sha256).hexdigest()
        return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)

    def handle_webhook(self, event: dict) -> str:
        data = event["data"]["object"]
        order_id = data["payment_intent"]

        match event["type"]:
            case constants.STRIPE_EVENT_PURCHASE_COMPLETED:
                checkout_session_id = data["id"]
                ret = self.register_order(order_id, checkout_session_id)

            case constants.STRIPE_EVENT_PURCHASE_REFUNDED:
                ret = json.dumps({"status": "error", "message": "no such purchase"})
                if order := utils.get_order(order_id):
                    if data["refunded"] and data["captured"] and data["paid"] and order.status != "refunded":
                        order.status = "refunded"
                        order.status_update_time = datetime.fromtimestamp(data["created"], UTC).isoformat()
                        utils.store_order(order)
                        ret = json.dumps({"status": "ok", "message": "purchase status updated"})
                    else:
                        ret = json.dumps({"status": "info", "message": "purchase unchanged"})

            case _:  # pragma: nocover
                ret = json.dumps({"status": "info", "message": "event not interesting"})

        return ret

    def fetch_order(self, kind: str, order_id: str) -> Order:
        url = constants.STRIPE_URL_CHECKOUT_SESSION.format(order_id)
        with SESSION.get(url, timeout=30) as req:
            req.raise_for_status()
            data = req.json()

        # client_reference_id contains `ULID-LANG_SRC-LANG_DST`
        reference = data.get("client_reference_id", "") or ""
        if reference.count("-") != 2:  # pragma: nocover
            msg = f"[stripe, order ID={data['payment_intent']!r}] client_reference_id unset or malformed: {reference!r}"
            raise ValueError(msg)
        ulid, name = reference.split("-", 1)

        order = Order(
            data["payment_intent"],
            dictionary=name,
            email=data["customer_email"] or data.get("customer_details", {}).get("email", ""),
            locale="en",
            source=self.source,
            status=purchase_status(data),
            status_update_time=datetime.fromtimestamp(data["created"], UTC).isoformat(),
            ulid=ulid,
            user=data.get("customer_details", {}).get("name", "").split(" ", 1)[0],
        )

        log.info("[order ID=%r] Stripe %s status is %s (valid: %s)", order.id, kind, order.status, order.status_ok)
        return order

    def register_order(self, order_id: str, checkout_session_id: str) -> str:
        if utils.get_order(order_id):
            log.info("Rejected purchase, order ID %r already exists", order_id)
            return json.dumps({"status": "info", "message": "purchase ID already exists"})

        order = self.fetch_order("purchase", checkout_session_id)
        if order.id != order_id:  # pragma: nocover
            log.error("[stripe] Rejected purchase, IDs do not concur: %r != %r", order.id, order_id)
            return json.dumps({"status": "error", "message": "order ID mismatch"})

        dict_key, dict_value = "name", order.dictionary
        if not utils.get_dictionary_from_key(dict_key, dict_value):  # pragma: nocover
            log.error("[stripe] Rejected purchase, %s=%r, order=%s", dict_key, dict_value, order)
            return json.dumps({"status": "error", "message": "invalid, or disabled, dictionary"})

        utils.store_order(order)

        with suppress(Exception):
            utils.send_email(order)

        return json.dumps({"status": "ok", "url": order.download_link})
