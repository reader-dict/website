from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import cached_property
from hashlib import pbkdf2_hmac

import ulid

from src import constants

log = logging.getLogger(__name__)
Dictionary = dict[str, bool | float | int | str]
Dictionaries = dict[str, dict[str, Dictionary]]
Link = tuple[str, str, str, str, str]
Reviews = list[dict[str, str]]


@dataclass
class Sponsor:
    amount: float
    date: str
    kind: str
    source: str
    end: str = ""
    message: str = ""
    repeat: str = ""
    public_name: str = ""
    url: str = ""

    def current_amount(self) -> float:
        if not (repeat := self.repeat):
            return self.amount

        assert repeat == "monthly", f"Invalid {repeat = }"  # noqa: S101

        end = datetime.fromisoformat(end) if (end := self.end) else datetime.now(tz=UTC)
        delta = end - datetime.fromisoformat(self.date)
        return self.amount * math.ceil((delta.days or 1) / (365.25 / 12))


Sponsors = dict[str, list[Sponsor]]


def make_ulid() -> str:
    return str(ulid.ULID())


def now() -> str:
    return datetime.now(tz=UTC).isoformat()


@dataclass()
class Order:
    id: str
    dictionary: str = ""
    dictionary_override: str = ""
    email: str = ""
    invoice_id: str = ""  # [purchase] PayPal capture ID, used to handle refunded purchase webhooks
    locale: str = "en"
    plan_id: str = ""  # [subscription]
    source: str = ""
    status: str = ""
    status_update_time: str = field(default_factory=now, compare=False)
    ulid: str = field(default_factory=make_ulid, compare=False)
    user: str = ""

    @cached_property
    def checkpoint(self) -> str:
        """Generate a *checkpoint* token to validate acces to dictionary downloads."""
        hash_name = "sha256"
        password = constants.PEPPER.join([self.dictionary, self.source, self.id])
        salt = self.ulid.encode() * 42
        iterations = 600_000
        return pbkdf2_hmac(hash_name, password.encode(), salt, iterations).hex()

    @property
    def download_link(self) -> str:
        return f"download/{self.lang_src}/{self.lang_dst}?order={self.id}&checkpoint={self.checkpoint}"

    @property
    def is_purchase(self) -> bool:
        return self.type == "purchase"

    @property
    def lang_dst(self) -> str:
        return self.target_dictionary.split("-", 1)[1]

    @property
    def lang_src(self) -> str:
        return self.target_dictionary.split("-", 1)[0]

    @property
    def status_ok(self) -> bool:
        if self.is_purchase:
            return self.status == "completed"

        # Subscription
        if self.status == "active":
            return True

        diff_time = datetime.now(tz=UTC) - datetime.fromisoformat(self.status_update_time)
        remaining_time = constants.ONE_MONTH - diff_time
        status_ok = remaining_time > constants.EXPIRED
        log.info(
            "[order ID=%r] PayPal subscription was %s on %s (%s left)",
            self.id,
            self.status,
            self.status_update_time,
            remaining_time,
        )
        log.info("[order ID=%r] PayPal subscription 1-month validity is %s", self.id, status_ok)
        return status_ok

    @property
    def target_dictionary(self) -> str:
        if self.dictionary_override:
            log.info("[order ID=%r] Dictionary override: %r -> %r", self.id, self.dictionary, self.dictionary_override)
            return self.dictionary_override
        return self.dictionary

    @cached_property
    def type(self) -> str:
        return "subscription" if self.plan_id else "purchase"

    def as_dict(self) -> dict:
        """Return only attributes that are actually defined."""
        return {
            key: value
            for key, value in vars(self).items()
            if key
            not in {
                "checkpoint",
                "download_link",
                "is_purchase",
                "lang_dst",
                "lang_src",
                "status_ok",
                "target_dictionary",
                "type",
            }
            and value != ""
        }
