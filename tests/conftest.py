import json
from pathlib import Path

import pytest
import responses

from src import constants, utils

from . import payloads


@pytest.fixture(autouse=True)
def isolate(tmp_path: Path) -> None:
    constants.ROOT = tmp_path
    constants.DATA = constants.ROOT / constants.DATA.name
    constants.DICTIONARIES = constants.DATA / constants.DICTIONARIES.name
    constants.REVIEWS = constants.DATA / constants.REVIEWS.name
    constants.FILES = constants.ROOT / constants.FILES.name
    constants.FILES_CACHE = constants.ROOT / constants.FILES_CACHE.name
    constants.CERTS = constants.FILES / constants.CERTS.name
    constants.LOGS = constants.ROOT / constants.LOGS.name
    constants.METRICS = constants.DATA / constants.METRICS.name
    constants.ORDERS = constants.DATA / constants.ORDERS.name

    constants.DATA.mkdir()
    constants.FILES.mkdir()
    constants.CERTS.mkdir()
    constants.FILES_CACHE.mkdir()

    utils.save_dictionaries(
        {
            "eo": {
                "eo": {
                    "enabled": True,
                    "formats": "df,dictorg,kobo,mobi,stardict",
                    "plan_id": "P-7DD30896GS809593MM735GMI",
                    "progress": "templates:62/62",
                    "uid": "01JRG0YZ81APV0ZTCNTHXYSRK9",
                    "updated": "2025-04-01",
                    "words": 17066,
                },
                "fr": {
                    "enabled": True,
                    "formats": "df,dictorg,kobo,mobi,stardict",
                    "plan_id": payloads.PLAN_ID,
                    "progress": "format:mobi;templates:2/42",
                    "uid": "01JR0WGRVP18RTFN6K57W42ZAX",
                    "updated": "2025-04-04",
                    "words": 151150,
                },
            }
        }
    )

    for lang_dst in ("eo", "fr"):
        folder = constants.FILES / "eo" / lang_dst
        folder.mkdir(parents=True)
        (folder / f"dict-eo-{lang_dst}.zip").write_bytes(b"AwEsOmE DiCt!")
        (folder / f"dicthtml-eo-{lang_dst}.zip").write_bytes(b"AwEsOmE DiCt!")
        (folder / f"dicthtml-eo-{lang_dst}.zip.sha256").write_bytes(b"ok")

    constants.REVIEWS.write_text(
        json.dumps(
            [
                {
                    "date": "2025-09-06",
                    "stars": 5,
                    "review": "Review text",
                    "reader": "Alice B.",
                    "device": "Kobo user",
                    "dictionaries": ["EO-FR"],
                },
                {
                    "date": "2025-09-07",
                    "stars": 4.9,
                    "review": "Review text 2",
                    "reader": "Bob C.",
                    "device": "Kindle user",
                    "dictionaries": ["EO-EO"],
                },
            ]
        )
    )


@pytest.fixture
def mock_responses() -> None:
    responses.post(constants.GITHUB_API_TRACKER, json=payloads.GITHUB_ISSUE)
    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(payloads.PAYPAL_CERT_URL, body=payloads.PAYPAL_CERT)
    responses.get(constants.PAYPAL_URL_PURCHASES.format(payloads.PURCHASE_ID), json=payloads.PURCHASE_DATA)
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(payloads.SUBSCRIPTION_ID), json=payloads.SUBSCRIPTION_DATA)
    responses.post(
        constants.STRIPE_URL_CHECKOUT_SESSION,
        json=payloads.STRIPE_CHECKOUT_SESSION_CREATE_DATA,
    )
    responses.get(
        f"{constants.STRIPE_URL_CHECKOUT_SESSION}/{payloads.STRIPE_CHECKOUT_SESSION_ID}",
        json=payloads.STRIPE_CHECKOUT_SESSION_DATA,
    )
