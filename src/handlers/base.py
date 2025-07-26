import abc
import json
import logging

from src import utils
from src.models import Order

log = logging.getLogger(__name__)


class Handler:
    source = "unset"

    @abc.abstractmethod
    def is_valid_webhook_event(self, headers: dict[str, str], payload: bytes) -> bool: ...

    @abc.abstractmethod
    def handle_webhook(self, event: dict) -> str: ...

    @abc.abstractmethod
    def _fetch_order_impl(self, kind: str, order_id: str) -> Order: ...

    def fetch_order(self, kind: str, order_id: str) -> Order:
        order = self._fetch_order_impl(kind, order_id)
        log.info(
            "[%s order ID=%r] %s status is %s (valid: %s)",
            self.source,
            order.id,
            kind,
            order.status,
            order.status_ok,
        )
        return order

    def register_order(self, order_id: str, checkout_session_id: str) -> str:
        if utils.get_order(order_id):
            log.info("Rejected purchase, order ID %r already exists", order_id)
            return json.dumps({"status": "info", "message": "purchase ID already exists"})

        order = self.fetch_order("purchase", checkout_session_id)
        if order.id != order_id:  # In case someone alters data between the webhook event and the order fetching
            log.error("[%s] Rejected purchase, IDs do not concur: %r != %r", self.source, order.id, order_id)
            return json.dumps({"status": "error", "message": "order ID mismatch"})

        utils.store_order(order)
        utils.send_email(order)

        return json.dumps({"status": "ok", "url": order.download_link})
