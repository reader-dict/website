import base64
import logging
import zlib
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any

import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from src import cache, constants, utils
from src.handlers import base
from src.models import Order

log = logging.getLogger(__name__)
SESSION = requests.Session()
TOKEN_CACHE_KEY = "paypal-access-token"  # noqa: S105


def access_token_refresher(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> requests.Response:  # noqa: ANN401
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                log.debug("Access token is expired, requesting a new one ...")
                cache.remove(TOKEN_CACHE_KEY)
                return func(*args, **kwargs)
            raise exc from None  # pragma: nocover

    return wrapper


def purchase_status(data: dict) -> str:
    if (status := data["status"]) == "COMPLETED":
        status = data["purchase_units"][0]["payments"]["captures"][0]["status"]
    return status.lower()


def get_access_token() -> str:
    try:
        access_token = cache.get_notimer(TOKEN_CACHE_KEY)
        log.debug("PayPal access token found in cache.")
    except cache.CacheMissError:
        log.debug("PayPal access token not found in cache.")
        with SESSION.post(
            constants.PAYPAL_URL_TOKEN,
            auth=(constants.PAYPAL_CLIENT_ID, constants.PAYPAL_CLIENT_SECRET),
            data="grant_type=client_credentials",
            headers=constants.HTTP_HEADERS | {"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        ) as req:
            access_token = req.json()["access_token"]
            cache.add_notimer(TOKEN_CACHE_KEY, access_token)
            log.debug("New PayPal access token acquired.")
    return access_token


def get_certificate(url: str) -> str:
    """Download the PayPal certificate."""
    try:
        paypal_cert = cache.get_notimer(url)
        log.info("PayPal certificate found in cache.")
    except cache.CacheMissError:
        log.info("PayPal certificate not found in cache.")
        with SESSION.get(url, timeout=30) as req:
            paypal_cert = req.text
            cache.add_notimer(url, paypal_cert)
    return paypal_cert


@access_token_refresher
def refund(capture_id: str, *, note: str = "") -> bool:  # pragma: nocover
    url = constants.PAYPAL_URL_PURCHASE_REFUND.format(capture_id)
    headers = {**constants.HTTP_HEADERS, "Authorization": f"Bearer {get_access_token()}"}
    data = {"invoice_id": capture_id}
    if note:
        data["note_to_payer"] = note

    with SESSION.post(url, headers=headers, json=data, timeout=30) as req:
        if req.status_code == 422:
            return True
        return req.ok and req.json()["status"] == "COMPLETED"


class Handler(base.Handler):
    source = "paypal"

    def is_valid_webhook_event(self, headers: dict[str, str], payload: bytes) -> bool:
        # Create the validation message
        transmission_id = headers["Paypal-Transmission-Id"]
        timestamp = headers["Paypal-Transmission-Time"]
        crc = zlib.crc32(payload)
        webhook_id = constants.PAYPAL_WEBHOOK_ID
        message = f"{transmission_id}|{timestamp}|{webhook_id}|{crc}"

        # Decode the base64-encoded signature from the header
        signature = base64.b64decode(headers["Paypal-Transmission-Sig"])

        # Load the certificate and extract the public key
        certificate = get_certificate(headers["Paypal-Cert-Url"])
        cert = x509.load_pem_x509_certificate(certificate.encode(), default_backend())
        public_key = cert.public_key()

        # Validate the message using the signature
        try:
            public_key.verify(signature, message.encode(), padding.PKCS1v15(), hashes.SHA256())
        except InvalidSignature:
            return False
        return True

    def handle_webhook(self, event: dict) -> dict[str, str]:  # noqa: PLR0911
        match event["event_type"]:
            case constants.PAYPAL_EVENT_PURCHASE_REFUNDED:
                invoice_id = event["resource"]["invoice_id"]
                if not (order := utils.get_order_from_invoice(invoice_id) or utils.get_order(invoice_id)):
                    return {"status": "error", "message": "no such purchase"}

                if order.status == "refunded":
                    return {"status": "info", "message": "purchase unchanged"}

                order.status = "refunded"
                order.status_update_time = datetime.now(tz=UTC).isoformat()
                utils.store_order(order)
                return {"status": "ok", "message": "purchase status updated"}

            case constants.PAYPAL_EVENT_SUBSCRIPTION_CANCELLED:
                if not (order := utils.get_order(event["resource"]["id"])):
                    return {"status": "error", "message": "no such subscription"}

                if order.status == (status := event["resource"]["status"].lower()):
                    return {"status": "info", "message": "subscription unchanged"}

                order.status = status
                order.status_update_time = event["resource"]["status_update_time"]
                utils.store_order(order)
                return {"status": "ok", "message": "subscription status updated"}

            case constants.PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED:
                if not (order := utils.get_order(event["resource"]["id"])):
                    return {"status": "error", "message": "no such subscription"}

                if order.status == "suspended":
                    return {"status": "info", "message": "subscription unchanged"}

                order.status = "suspended"
                order.status_update_time = event["resource"]["update_time"]
                utils.store_order(order)
                return {"status": "ok", "message": "subscription status updated"}

        return {"status": "info", "message": "event not interesting"}

    @access_token_refresher
    def _fetch_order_impl(self, kind: str, order_id: str) -> Order:
        url = getattr(constants, f"PAYPAL_URL_{kind.upper()}S").format(order_id)
        headers = constants.HTTP_HEADERS | {"Authorization": f"Bearer {get_access_token()}"}

        with SESSION.get(url, headers=headers, timeout=30) as req:
            req.raise_for_status()
            data = req.json()

        order = Order(order_id, status_update_time=data["update_time" if kind == "purchase" else "status_update_time"])
        if kind == "purchase":
            order.email = data["payer"].get("email_address", "")
            order.invoice_id = data["purchase_units"][0]["payments"]["captures"][0]["id"]
            order.user = data["payer"]["name"]["given_name"]
            order.dictionary = data["purchase_units"][0]["items"][0]["sku"]
            order.status = purchase_status(data)
        else:
            order.email = data["subscriber"].get("email_address", "")
            order.plan_id = data["plan_id"]
            order.status = data["status"].lower()
            order.user = data["subscriber"]["name"]["given_name"]
        return order
