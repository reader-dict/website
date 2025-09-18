import pytest
from freezegun import freeze_time

from src.models import Order


@freeze_time("2025-09-18T11:19:16+02:00")
def test_as_dict() -> None:
    order = Order("some-id", dictionary="eo-fr", source="paypal", status="completed")
    assert order.checkpoint
    assert order.as_dict() == {
        "dictionary": "eo-fr",
        "id": "some-id",
        "locale": "en",
        "source": "paypal",
        "status": "completed",
        "status_update_time": "2025-09-18T09:19:16+00:00",
        "ulid": order.ulid,
    }


def test_properties() -> None:
    order = Order("some-id", dictionary="eo-fr", source="paypal", ulid="01JR40E9TR91RNE11Z6BPSP8W4")
    checkpoint = "d99b989c762a4d70a645f005564eea18702f83f21c65411ce784658c7bb7cb4d"

    assert order.download_link == f"download/eo/fr?order={order.id}&checkpoint={checkpoint}"
    assert order.checkpoint == checkpoint
    assert order.target_dictionary == "eo-fr"

    order.dictionary_override = "eo-eo"
    assert order.target_dictionary == "eo-eo"


@freeze_time("2025-04-14T17:02:31Z")
@pytest.mark.parametrize(
    ("end", "expected"),
    [
        ("2025-04-14T17:02:31Z", True),
        ("2025-02-14T17:02:31Z", False),
    ],
)
def test_subscription_still_ongoing(end: str, expected: bool) -> None:
    assert Order("sime-id", plan_id="plan-id", status_update_time=end).status_ok is expected
