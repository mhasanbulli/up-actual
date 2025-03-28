from datetime import datetime

import pytest
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


def test_get_rfc_3339_date_offset():
    start_date = datetime(2023, 10, 10, 12, 0, 0)
    days_offset = 5
    expected_date = "2023-10-05T12:00:00+11:00"

    result = get_rfc_3339_date_offset(start_date, days_offset)

    assert result == expected_date
