from datetime import datetime

import pytest
import pytz
from up.utils import get_rfc_3339_date_offset, get_token


@pytest.mark.parametrize("token", ["", "up-token"])
def test_get_token(monkeypatch: pytest.MonkeyPatch, token: str):
    monkeypatch.setenv("UP_TOKEN", token)

    up_token = get_token()

    if token:
        assert up_token == "up-token"
    elif token is None:
        with pytest.raises(OSError) as excinfo:
            get_token()

        assert excinfo.value == "UP_TOKEN environment variable is not set."


@pytest.mark.parametrize(
    "start_date, days_offset, expected_date",
    [
        # Standard time (non-DST period)
        (
            pytz.timezone("Australia/Melbourne").localize(datetime(2023, 7, 10, 12, 0, 0)),
            5,
            "2023-07-05T12:00:00+10:00",
        ),
        # DST transition period
        (
            pytz.timezone("Australia/Melbourne").localize(datetime(2023, 10, 10, 12, 0, 0)),
            5,
            "2023-10-05T12:00:00+11:00",
        ),
    ],
)
def test_get_rfc_3339_date_offset(start_date: datetime, days_offset: int, expected_date: str):
    result = get_rfc_3339_date_offset(start_date, days_offset)
    assert result == expected_date
