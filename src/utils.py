import fcntl
import functools
import imaplib
import json
import logging
import shutil
import smtplib
from collections.abc import Callable
from datetime import UTC, datetime
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid
from math import floor
from typing import Any

from src import cache, constants, translations
from src.models import Dictionaries, Dictionary, Link, Order

log = logging.getLogger(__name__)


def best_price(dictionary: Dictionary) -> float:
    """Most appropriate subscription price based on the words count.

    Grid:
               0 - 500      = 0.99 €
             500 - 1000     = 1.49 €
            1000 - 10000    = 2.49 €
           10000 - 100000   = 3.49 €
          100000 - 1000000  = 4.49 €
        10000000 - 20000000 = 5.49 €
        20000000 - 30000000 = 6.49 €
        30000000 - 40000000 = 7.49 €
        40000000 - 50000000 = 8.49 €
        50000000 - 60000000 = 9.49 €
    """
    if (words := int(dictionary["words"])) == 0:
        return 0.0
    if (level := next((float(idx) for idx, lvl in enumerate(constants.PRICE_LEVELS) if words in lvl))) == 0.0:
        return 0.99
    return level + 0.49


def best_price_for_purchase(dictionary: Dictionary, *, multiplier: float = 1 / 0.01) -> float:
    """Most appropriate one-time purchase price based on the subscription price.

    Grid:
               0 - 500      = 0.99 +  1 €
             500 - 1000     = 1.49 +  2 €
            1000 - 10000    = 2.49 +  3 €
           10000 - 100000   = 3.49 +  4 €
          100000 - 1000000  = 4.49 +  5 €
        10000000 - 20000000 = 5.49 +  6 €
        20000000 - 30000000 = 6.49 +  7 €
        30000000 - 40000000 = 7.49 +  8 €
        40000000 - 50000000 = 8.49 +  9 €
        50000000 - 60000000 = 9.49 + 10 €
    """
    words = int(dictionary["words"])
    level = next((float(idx) for idx, lvl in enumerate(constants.PRICE_LEVELS, 1) if words in lvl), 0.0)
    return floor((best_price(dictionary) + level) * multiplier) / multiplier


def craft_downloads_url(dictionary: Dictionary, *, order_type: str = "", order_id: str = "") -> dict[str, Link]:
    lang_src, lang_dst = str(dictionary["name"]).split("-", 1)
    mono = lang_src == lang_dst
    available_formats = str(dictionary["formats"]).split(",")
    links: dict[str, Link] = {}

    for fmt, (pretty_fmt, pattern) in constants.DICTIONARY_FORMATS.items():
        if fmt not in available_formats:
            continue

        file_name_full = pattern.format(lang_src=lang_src, lang_dst=lang_dst, etym_suffix="")
        file_name_noetym = pattern.format(lang_src=lang_src, lang_dst=lang_dst, etym_suffix="-noetym")
        if not order_id and mono:
            link_full = f"{lang_src}/{file_name_full}"
            link_noetym = f"{lang_src}/{file_name_noetym}"
        else:
            link_full = cache.add(order_type, order_id, lang_src, lang_dst, file_name_full, fmt)
            link_noetym = cache.add(order_type, order_id, lang_src, lang_dst, file_name_noetym, fmt)
        links[fmt] = (pretty_fmt, file_name_full, file_name_noetym, link_full, link_noetym)

    return links


def get_format_from_file_name(lang: str, name: str) -> str:
    for fmt, (_, pattern) in constants.DICTIONARY_FORMATS.items():
        if (
            pattern.format(lang_src=lang, lang_dst=lang, etym_suffix="") == name
            or pattern.format(lang_src=lang, lang_dst=lang, etym_suffix="-noetym") == name
        ):
            return fmt
    raise FileNotFoundError


def get_dictionaries() -> Dictionaries:
    return json.loads(constants.DICTIONARIES.read_text())


def get_dictionary_from_key(key: str, value: str) -> Dictionary:
    """Find the dictionary related to the given `key`."""
    for langs in load_dictionaries().values():
        for details in langs.values():
            if details[key] == value:
                return details
    return {}


def get_dictionary_from_langs(langs_pair: str) -> Dictionary:
    """Find the dictionary related to the given `lang` (`lang_src-lang_dst` pair)."""
    if "-" not in langs_pair:
        return {}

    lang_src, lang_dst = langs_pair.split("-", 1)
    try:
        return load_dictionaries()[lang_src][lang_dst]
    except KeyError:
        return {}


def get_dictionary_metadata(order: Order, lang_src: str, lang_dst: str) -> Dictionary:
    if order.is_purchase:
        file = constants.PURCHASE_FILES / order.id / "metadata.json"
        try:
            return json.loads(file.read_text()) | {"name": f"{lang_src}-{lang_dst}"}
        except FileNotFoundError:
            return {}

    try:
        return load_dictionaries()[lang_src][lang_dst]
    except KeyError:
        return {}


def is_checkpoint(checkpoint: str) -> bool:
    if not checkpoint or len(checkpoint) != 64:
        return False
    try:
        int(checkpoint, 16)
    except ValueError:
        return False
    return True


def load_dictionaries() -> Dictionaries:
    """Load public-ready dictionaries."""
    return {
        lang_src: {
            lang_dst: {k: v for k, v in details.items() if k in constants.DICTIONARY_KEYS}
            | {"name": f"{lang_src}-{lang_dst}"}
            for lang_dst, details in langs.items()
            if details.get("plan_id") and details.get("enabled") and details.get("uid")
        }
        for lang_src, langs in get_dictionaries().items()
        if any(details.get("plan_id") and details.get("enabled") and details.get("uid") for details in langs.values())
    }


def save_dictionaries(dictionaries: Dictionaries) -> None:
    """Save dictionaries."""
    constants.DICTIONARIES.write_text(
        json.dumps(
            dictionaries,
            ensure_ascii=False,
            check_circular=False,
            indent=4,
            sort_keys=True,
        )
    )


def load_orders() -> dict[str, Order]:
    """Load purchases, and subscriptions."""
    try:
        return {uid: Order(**obj) for uid, obj in json.loads(constants.ORDERS.read_text()).items()}
    except (FileNotFoundError, ValueError):
        return {}


def get_order(uid: str) -> Order | None:
    return load_orders().get(uid)


def get_order_from_invoice(invoice_id: str) -> Order | None:
    return next((order for order in load_orders().values() if order.invoice_id == invoice_id), None)


def locker(kind: str) -> Callable:
    """File locking mechanism to protect against concurrent read/write mess."""

    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:  # noqa: ANN401
            with (constants.FILES_CACHE / f"{kind}.lock").open(mode="w") as fh:
                fcntl.flock(fh, fcntl.LOCK_EX)
                try:
                    return function(*args, **kwargs)
                finally:
                    fcntl.flock(fh, fcntl.LOCK_UN)

        return wrapper

    return decorator


def persist_data(order: Order) -> bool:
    folder = constants.PURCHASE_FILES / order.id
    metadata_file = folder / "metadata.json"

    if metadata_file.is_file():
        log.debug("Files already persisted")
        return False

    folder.mkdir(exist_ok=True, parents=True)

    # Copy dictionary files
    tree = shutil.copytree(constants.FILES / order.lang_src / order.lang_dst, folder, dirs_exist_ok=True)
    log.debug("Cloned tree %s", tree)

    # Copy dictionary metadata
    metadata = get_dictionaries()[order.lang_src][order.lang_dst]
    metadata["buy-date"] = datetime.now(tz=UTC).isoformat()
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=4, sort_keys=True))
    log.debug("Wrote metadata.json with %s", metadata)
    return True


def send_email(order: Order) -> bool:
    if not order.email:
        log.error("[email order ID=%r] No email address provided!", order.id)
        return False

    lang_src, lang_dst = order.lang_src, order.lang_dst
    sig_www = f"https://www.{constants.WWW}"
    link = f"{sig_www}/{order.download_link}"
    now = datetime.now(tz=UTC)
    sig_text = f"© {constants.PROJECT} {now.year}"
    name = order.user
    addr_to = order.email

    msg = EmailMessage()
    msg["Subject"] = tr("email-subject", lang_src.upper(), lang_dst.upper())
    msg["From"] = Address(display_name=constants.PROJECT, username="noreply", domain=constants.WWW)
    msg["To"] = Address(display_name=name, addr_spec=addr_to)
    msg["Reply-To"] = f"contact@{constants.WWW}"
    msg["Message-ID"] = make_msgid()

    # Plan text message
    msg.set_content(tr("email-content-txt", name, link, sig_text, sig_www))

    # HTML version
    msg.add_alternative(tr("email-content-html", name, link, sig_text, sig_www), subtype="html")

    # Make a local copy of what we are going to send
    constants.EMAILS.mkdir(exist_ok=True)
    (constants.EMAILS / f"{order.id}.msg").write_bytes(bytes(msg))

    if not constants.SMTP_PASSWORD:
        log.warning("[email order ID=%r] No SMTP password defined! Email saved but not sent.", order.id)
        return False

    # Send the message
    ret = True
    try:
        with smtplib.SMTP_SSL(host=f"mail.{constants.WWW}", port=465, timeout=30) as smtp:
            smtp.login(f"noreply@{constants.WWW}", constants.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception:
        log.exception("[email order ID=%r] Could not send the email to %s at %s!", order.id, name, addr_to)
        ret = False
    else:
        log.info("[email order ID=%r] Email sent to %s at %s", order.id, name, addr_to)

    # Finally, keep a copy into the Sent folder
    try:
        with imaplib.IMAP4_SSL(host=f"mail.{constants.WWW}", port=993, timeout=30) as imap:
            imap.login(f"noreply@{constants.WWW}", constants.SMTP_PASSWORD)
            imap.append("INBOX.Sent", "\\Seen", imaplib.Time2Internaldate(now.timestamp()), bytes(msg))
    except Exception:
        log.exception(
            "[email order ID=%r] Could not keep a copy of the email sent to %s at %s!",
            order.id,
            name,
            addr_to,
        )
        ret = False
    else:
        log.info("[email order ID=%r] Kept an email copy.", order.id)

    return ret


@locker("orders")
def store_order(order: Order) -> None:
    """Store a purchase, or a subscription. If the order already exists, its details will be updated."""
    orders = load_orders() | {order.id: order}
    constants.ORDERS.write_text(
        json.dumps({uid: obj.as_dict() for uid, obj in orders.items()}, sort_keys=True, indent=4)
    )


@functools.cache
def tr(key: str, *args: str) -> str:
    """Translations."""
    try:
        value = translations.translations[key]
    except KeyError:
        log.exception("Missing translation key %r", key)
        return key
    return value.format(*args) if args else value
