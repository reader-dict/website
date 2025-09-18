import fcntl
import functools
import imaplib
import json
import logging
import smtplib
from collections.abc import Callable
from datetime import UTC, datetime
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid
from random import sample
from typing import Any

from src import cache, constants, languages
from src.models import Dictionaries, Dictionary, Link, Order, Reviews, Sponsor, Sponsors

log = logging.getLogger(__name__)


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


def create_dictionary_links(reviews: list[dict]) -> list[dict]:
    for review in reviews:
        dictionaries = []
        for dictionary in review["dictionaries"]:
            lang_src, lang_dst = dictionary.split("-", 1)
            if lang_src == lang_dst:
                lang = lang_src.lower()
                link = f'<a class="unstyled" href="/download/{lang}" title="Acquire the awesome {language(lang)} dictionary for free">{dictionary}</a>'  # noqa: E501
            else:
                link = f'<a class="unstyled" href="/#{dictionary.lower()}" title="Acquire the awesome {language(lang_src.lower())} - {language(lang_dst.lower())} dictionary">{dictionary}</a>'  # noqa: E501
            dictionaries.append(link)
        review["dictionaries"] = dictionaries
    return reviews


def get_format_from_file_name(lang: str, name: str) -> str:
    for fmt, (_, pattern) in constants.DICTIONARY_FORMATS.items():
        if (
            pattern.format(lang_src=lang, lang_dst=lang, etym_suffix="") == name
            or pattern.format(lang_src=lang, lang_dst=lang, etym_suffix="-noetym") == name
        ):
            return fmt
    raise FileNotFoundError


def get_dictionaries() -> Dictionaries:
    return json.loads(constants.DICTIONARIES.read_text(encoding=constants.ENCODING))


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


def get_dictionary_metadata(lang_src: str, lang_dst: str) -> Dictionary:
    try:
        return load_dictionaries()[lang_src][lang_dst]
    except KeyError:
        return {}


def get_faq() -> dict[str, str]:
    return json.loads(constants.FAQ.read_text(encoding=constants.ENCODING))


def get_last_modification_time(dictionary: Dictionary) -> str:
    """Return the last modified time of the given `dictionary` StarDict file."""
    lang_src, lang_dst = str(dictionary["name"]).split("-", 1)
    stardict = constants.DICTIONARY_FORMATS["stardict"][1].format(lang_src=lang_src, lang_dst=lang_dst, etym_suffix="")
    file = constants.FILES / lang_src / lang_dst / stardict
    return datetime.fromtimestamp(file.stat().st_mtime, tz=UTC).strftime("%Y-%m-%d %H:%M UTC")


def get_sponsors() -> Sponsors:
    return {
        name: [Sponsor(**donation) for donation in donations]
        for name, donations in json.loads(constants.SPONSORS.read_text(encoding=constants.ENCODING)).items()
    }


def is_checkpoint(checkpoint: str) -> bool:
    if not checkpoint or len(checkpoint) != 64:
        return False
    try:
        int(checkpoint, 16)
    except ValueError:
        return False
    return True


def is_dict_enabled(dictionary: Dictionary) -> bool:
    return (
        int(dictionary["words"]) >= constants.MINIMUM_REQUIRED_WORDS
        and bool(dictionary.get("formats", ""))
        and bool(dictionary.get("uid", ""))
    )


def load_dictionaries(*, keys: list[str] = constants.DICTIONARY_KEYS_ALL) -> Dictionaries:
    """Load public-ready dictionaries."""
    name_wanted = "name" in keys
    return {
        lang_src: {
            lang_dst: {k: v for k, v in dictionary.items() if k in keys}
            | ({"name": f"{lang_src}-{lang_dst}"} if name_wanted else {})
            for lang_dst, dictionary in langs.items()
            if is_dict_enabled(dictionary)
        }
        for lang_src, langs in get_dictionaries().items()
        if any(is_dict_enabled(dictionary) for dictionary in langs.values())
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
        return {
            uid: Order(**obj)
            for uid, obj in json.loads(constants.ORDERS.read_text(encoding=constants.ENCODING)).items()
        }
    except (FileNotFoundError, ValueError):
        return {}


def get_order(uid: str) -> Order | None:
    return load_orders().get(uid)


def get_order_from_invoice(invoice_id: str) -> Order | None:
    return next((order for order in load_orders().values() if order.invoice_id == invoice_id), None)


def load_sponsors() -> dict[str, list[tuple[str, str, float]]]:
    """Load sponsors."""
    ret: dict[str, list[tuple[str, str, float]]] = {
        "diamond": [],
        "titanium": [],
        "platinium": [],
        "gold": [],
    }
    for name, donations in get_sponsors().items():
        amount = 0.0
        public_name = name
        url = ""
        for donation in donations:
            amount += donation.current_amount()
            url = donation.url or url
            public_name = donation.public_name or public_name
        tiers = (
            "diamond" if amount >= 1000 else "titanium" if amount >= 300 else "platinium" if amount >= 100 else "gold"
        )
        ret[tiers].append((public_name, url, amount))
    return ret


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


def random_reviews(count: int) -> Reviews:
    """Load `count` random reviews."""
    all_reviews = json.loads(constants.REVIEWS.read_text(encoding=constants.ENCODING))
    return sample(all_reviews, count)


def send_email(order: Order) -> bool:
    if not order.email:
        log.error("[email order ID=%r] No email address provided!", order.id)
        return False

    lang_src, lang_dst = language(order.lang_src), language(order.lang_dst)
    sig_www = f"https://www.{constants.WWW}"
    link = f"{sig_www}/{order.download_link}"
    now = datetime.now(tz=UTC)
    sig_text = f"© {constants.PROJECT} {now.year}"
    name = order.user
    addr_to = order.email
    title = f"{lang_src} {lang_dst}" if order.lang_src == "all" else f"{lang_src} - {lang_dst}"

    msg = EmailMessage()
    msg["Subject"] = constants.EMAIL_SUBJECT.format(title)
    msg["From"] = Address(display_name=constants.PROJECT, username="noreply", domain=constants.WWW)
    msg["To"] = Address(display_name=name, addr_spec=addr_to)
    msg["Reply-To"] = f"contact@{constants.WWW}"
    msg["Message-ID"] = make_msgid()

    # Plain text message
    msg.set_content(constants.EMAIL_BODY_TXT.format(name, link, sig_text, sig_www))

    # HTML version
    msg.add_alternative(constants.EMAIL_BODY_HTML.format(name, link, sig_text, sig_www), subtype="html")

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
def language(key: str) -> str:
    """Languages in English."""
    try:
        return languages.languages[key]
    except KeyError:
        log.exception("Missing language name for %r", key)
        return key
