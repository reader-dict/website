import base64
import json
import logging
import zlib
from collections.abc import Callable
from contextlib import suppress
from copy import deepcopy
from datetime import UTC, datetime
from functools import wraps
from typing import Any

import requests
import ulid
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from src import cache, constants, utils
from src.models import Order

log = logging.getLogger(__name__)
SESSION = requests.Session()


def access_token_refresher(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> requests.Response:  # noqa: ANN401
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                log.debug("Access token is expired, requesting a new one ...")
                cache.remove("access-token")
                return func(*args, **kwargs)
            raise exc from None  # pragma: nocover

    return wrapper


def register_order(kind: str, order_id: str) -> str:
    """Register a new purchase, or subscription."""
    if utils.get_order(order_id):
        log.info("Rejected %s, order ID %r already exists", kind, order_id)
        return json.dumps({"status": "info", "message": f"{kind} ID already exists"})

    order = fetch_order(kind, order_id)

    dict_key, dict_value = ("name", order.dictionary) if order.is_purchase else ("plan_id", order.plan_id)
    if not (dictionary := utils.get_dictionary_from_key(dict_key, dict_value)):
        log.error("Rejected PayPal %s, %s=%r, order=%s", kind, dict_key, dict_value, order)
        return json.dumps({"status": "error", "message": "invalid, or disabled, dictionary"})

    order.dictionary = dictionary["name"]
    order.source = "paypal"
    utils.store_order(order)

    if order.is_purchase:
        utils.persist_data(order)

    with suppress(Exception):
        utils.send_email(order)

    return json.dumps({"status": "ok", "url": order.download_link})


@access_token_refresher
def fetch_order(kind: str, order_id: str) -> Order:
    """Fetch purchase/subscription details."""
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

    log.info("[order ID=%r] PayPal purchase status is %s (valid: %s)", order.id, order.status, order.status_ok)
    return order


def purchase_status(data: dict) -> str:
    if (status := data["status"]) == "COMPLETED":
        status = data["purchase_units"][0]["payments"]["captures"][0]["status"]
    return status.lower()


def get_access_token() -> str:
    try:
        access_token = cache.get_notimer("access-token")
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
            cache.add_notimer("access-token", access_token)
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


def handle_webhook(event: dict) -> str:  # noqa: PLR0912,C901
    match event["event_type"]:
        case constants.PAYPAL_EVENT_PURCHASE_COMPLETED | constants.PAYPAL_EVENT_SUBSCRIPTION_COMPLETED:
            try:
                order_id = event["resource"]["supplementary_data"]["related_ids"]["order_id"]
                kind = "purchase"
            except KeyError:
                order_id = event["resource"]["billing_agreement_id"]
                kind = "subscription"
            ret = register_order(kind, order_id)

        case constants.PAYPAL_EVENT_PURCHASE_REFUNDED:
            invoice_id = event["resource"]["invoice_id"]
            if order := utils.get_order_from_invoice(invoice_id) or utils.get_order(invoice_id):
                if order.status != "refunded":
                    order.status = "refunded"
                    order.status_update_time = datetime.now(tz=UTC).isoformat()
                    utils.store_order(order)
                    ret = json.dumps({"status": "ok", "message": "purchase status updated"})
                else:
                    ret = json.dumps({"status": "info", "message": "purchase unchanged"})
            else:
                ret = json.dumps({"status": "error", "message": "no such purchase"})

        case constants.PAYPAL_EVENT_SUBSCRIPTION_CANCELLED:
            if order := utils.get_order(event["resource"]["id"]):
                if order.status != (status := event["resource"]["status"].lower()):
                    order.status = status
                    order.status_update_time = event["resource"]["status_update_time"]
                    utils.store_order(order)
                    ret = json.dumps({"status": "ok", "message": "subscription status updated"})
                else:
                    ret = json.dumps({"status": "info", "message": "subscription unchanged"})
            else:
                ret = json.dumps({"status": "error", "message": "no such subscription"})

        case constants.PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED:
            if order := utils.get_order(event["resource"]["id"]):
                if order.status != "suspended":
                    order.status = "suspended"
                    order.status_update_time = event["resource"]["update_time"]
                    utils.store_order(order)
                    ret = json.dumps({"status": "ok", "message": "subscription status updated"})
                else:
                    ret = json.dumps({"status": "info", "message": "subscription unchanged"})
            else:
                ret = json.dumps({"status": "error", "message": "no such subscription"})

        case constants.PAYPAL_EVENT_PURCHASE_APPROVED | constants.PAYPAL_EVENT_SUBSCRIPTION_CREATED:
            ret = json.dumps({"status": "info", "message": "event not interesting"})

        case _:
            msg = "Unhandled PayPal webhook"
            raise ValueError(msg)

    return ret


def is_valid_webhook_event(headers: dict[str, str], payload: bytes) -> bool:
    """Validate a PayPal webhook event."""
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


def craft_billing_cycle(price: float) -> dict:
    return {
        "frequency": {"interval_unit": "MONTH", "interval_count": 1},
        "tenure_type": "REGULAR",
        "sequence": 1,
        "total_cycles": 0,
        "pricing_scheme": {"fixed_price": {"value": price, "currency_code": "EUR"}},
    }


@access_token_refresher
def create_plan(lang_src: str, lang_dst: str, price: float) -> tuple[str, str]:
    """Create a plan for a given `lang_src-lang_dst` pair."""
    product = f"{constants.PROJECT} {lang_src.upper()}-{lang_dst.upper()}"
    kind = "monolingual" if lang_src == lang_dst else "universal" if lang_src == "all" else "bilingual"

    headers = {**constants.HTTP_HEADERS, "Authorization": f"Bearer {get_access_token()}", "Prefer": "return=minimal"}
    data = {
        "product_id": "reader-dict",
        "name": f"{product} ({kind})",
        "description": product,
        "status": "ACTIVE",
        "billing_cycles": [craft_billing_cycle(price)],
        "payment_preferences": {"payment_failure_threshold": 1},
    }

    with SESSION.post(constants.PAYPAL_URL_PLAN, headers=headers, json=data, timeout=30) as req:
        req.raise_for_status()
        return req.json()["id"], str(ulid.ULID())


def create_all_plans() -> None:  # pragma: nocover
    dictionaries = utils.get_dictionaries()
    updated_dictionaries = deepcopy(dictionaries)

    with suppress(Exception):
        for lang_src, langs_dst in deepcopy(dictionaries).items():
            for lang_dst, details in langs_dst.items():
                if details.get("plan_id"):
                    continue

                words = details["words"]

                if not words:
                    if not details.get("uid"):
                        updated_dictionaries[lang_src][lang_dst].update(
                            {
                                "enabled": False,
                                "plan_id": "",
                                "price": 0.0,
                                "price_purchase": 0.0,
                                "uid": str(ulid.ULID()),
                            }
                        )
                    continue

                price = utils.best_price(details)
                print(f"{lang_src}-{lang_dst}".upper(), f"({words:,} words) [{price:.2f} €]", flush=True)
                plan_id, uid = create_plan(lang_src, lang_dst, price)
                updated_dictionaries[lang_src][lang_dst].update(
                    {
                        # Dictionaries with less than 100 words are not worth sharing, I guess
                        "enabled": int(words) > 100,
                        "plan_id": plan_id,
                        "price": price,
                        "price_purchase": utils.best_price_for_purchase(details),
                        "uid": uid,
                    }
                )

    if dictionaries != updated_dictionaries:
        utils.save_dictionaries(updated_dictionaries)


@access_token_refresher
def update_plan(plan_id: str, new_price: float) -> None:  # pragma: nocover
    """Update the price of a given `plan_id`."""
    headers = {**constants.HTTP_HEADERS, "Authorization": f"Bearer {get_access_token()}"}
    data = {"pricing_schemes": [{"billing_cycle_sequence": 1, **craft_billing_cycle(new_price)}]}

    with SESSION.post(constants.PAYPAL_URL_PRICE.format(plan_id), headers=headers, json=data, timeout=30) as req:
        if req.status_code not in {204, 422}:
            req.raise_for_status()


def update_all_plans() -> None:  # pragma: nocover
    dictionaries = utils.get_dictionaries()
    updated_dictionaries = deepcopy(dictionaries)

    with suppress(Exception):
        for lang_src, langs_dst in updated_dictionaries.items():
            for lang_dst, details in langs_dst.items():
                words = int(details["words"])

                if not words:
                    if not details.get("uid"):
                        details["uid"] = str(ulid.ULID())
                    continue

                if (current_price := float(details.get("price", 0.0))) != (price := utils.best_price(details)):
                    print(
                        f"{lang_src}-{lang_dst}".upper(),
                        details["plan_id"],
                        f"[subscription {current_price:.2f} → {price:.2f} €]",
                        flush=True,
                    )
                    update_plan(str(details["plan_id"]), price)
                    details["price"] = price

                if (current_price_purchase := float(details.get("price_purchase", 0.0))) != (
                    price_purchase := utils.best_price_for_purchase(details)
                ):
                    print(
                        f"{lang_src}-{lang_dst}".upper(),
                        details["plan_id"],
                        f"[purchase {current_price_purchase:.2f} → {price_purchase:.2f} €]",
                        flush=True,
                    )
                    details["price_purchase"] = price_purchase

                # Dictionaries with less than 100 words are not worth sharing, I guess
                details["enabled"] = words > 100

    if dictionaries != updated_dictionaries:
        utils.save_dictionaries(updated_dictionaries)


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
