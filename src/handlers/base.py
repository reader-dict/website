import abc
import logging

from src.models import Order

log = logging.getLogger(__name__)


class Handler:
    source = "unset"

    @abc.abstractmethod
    def is_valid_webhook_event(self, headers: dict[str, str], payload: bytes) -> bool: ...

    @abc.abstractmethod
    def handle_webhook(self, event: dict) -> str: ...

    @abc.abstractmethod
    def fetch_order(self, kind: str, order_id: str) -> Order: ...
