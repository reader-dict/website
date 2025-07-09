from pathlib import Path

import pytest
import responses

from src import constants, utils

from . import payloads


@pytest.fixture(autouse=True)
def isolate(tmp_path: Path) -> None:
    constants.ROOT = tmp_path
    constants.DATA = constants.ROOT / constants.DATA.name
    constants.FILES = constants.ROOT / constants.FILES.name
    constants.FILES_CACHE = constants.ROOT / constants.FILES_CACHE.name
    constants.CERTS = constants.FILES / constants.CERTS.name
    constants.EMAILS = constants.DATA / constants.EMAILS.name
    constants.LOGS = constants.ROOT / constants.LOGS.name
    constants.METRICS = constants.DATA / constants.METRICS.name
    constants.ORDERS = constants.DATA / constants.ORDERS.name
    constants.PURCHASE_FILES = constants.FILES / constants.PURCHASE_FILES.name
    constants.DICTIONARIES = constants.DATA / constants.DICTIONARIES.name

    constants.DATA.mkdir()
    constants.FILES.mkdir()
    constants.CERTS.mkdir()
    constants.FILES_CACHE.mkdir()
    constants.EMAILS.mkdir()

    constants.SMTP_PASSWORD = ""
    constants.PEPPER = "Red Hot Chili Peppers"

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
        (folder / f"dicthtml-eo-{lang_dst}.zip").write_bytes(b"AwEsOmE DiCt!")
        (folder / f"dicthtml-eo-{lang_dst}.zip.sha256").write_bytes(b"ok")


@pytest.fixture
def mock_responses() -> None:
    responses.post(constants.GITHUB_API_TRACKER, json=payloads.GITHUB_ISSUE)
    responses.post(constants.PAYPAL_URL_TOKEN, json={"access_token": "token"})
    responses.get(payloads.PAYPAL_CERT_URL, body=payloads.PAYPAL_CERT)
    responses.post(constants.PAYPAL_URL_PLAN, json={"id": "new-plan-id"})
    responses.get(constants.PAYPAL_URL_PURCHASES.format(payloads.PURCHASE_ID), json=payloads.PURCHASE_DATA)
    responses.get(constants.PAYPAL_URL_SUBSCRIPTIONS.format(payloads.SUBSCRIPTION_ID), json=payloads.SUBSCRIPTION_DATA)
