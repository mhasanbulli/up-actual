from datetime import datetime
from pathlib import Path

import pytest
import pytz
import ujson
from jsonschema import ValidationError
from up.utils import get_rfc_3339_date_offset, get_token, get_url, load_json, schema_validator


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


def test_get_token_not_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("UP_TOKEN", raising=False)

    with pytest.raises(OSError, match=r"UP_TOKEN environment variable is not set\."):
        get_token()


def test_get_url_no_params():
    base_url = "https://api.example.com/endpoint"
    result = get_url(base_url, None)
    assert result == base_url


def test_get_url_with_params():
    base_url = "https://api.example.com/endpoint"
    params = {"page": "1", "size": "100"}
    result = get_url(base_url, params)
    assert "page=1" in result
    assert "size=100" in result


def test_get_url_with_none_values():
    base_url = "https://api.example.com/endpoint"
    params = {"page": "1", "filter": None, "size": "100"}
    result = get_url(base_url, params)
    assert "page=1" in result
    assert "size=100" in result
    assert "filter" not in result


def test_get_url_with_list_values():
    base_url = "https://api.example.com/endpoint"
    params = {"tags": ["tag1", "tag2"]}
    result = get_url(base_url, params)
    assert "tags=tag2" in result


def test_get_url_empty_params():
    base_url = "https://api.example.com/endpoint"
    params = {}
    result = get_url(base_url, params)
    assert result == base_url


def test_load_json(tmp_path: Path):
    test_data = {"key": "value", "number": 42}
    test_file = tmp_path / "test.json"

    with test_file.open("w", encoding="utf-8") as f:
        ujson.dump(test_data, f)

    result = load_json(test_file)
    assert result == test_data


def test_schema_validator_valid():
    instance = {"name": "Test", "age": 30}
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }

    schema_validator(instance, schema)


def test_schema_validator_invalid():
    instance = {"name": "Test", "age": "thirty"}
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }

    with pytest.raises(ValidationError):
        schema_validator(instance, schema)


def test_schema_validator_missing_required():
    instance = {"name": "Test"}
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }

    with pytest.raises(ValidationError):
        schema_validator(instance, schema)


def test_get_rfc_3339_date_offset_zero_offset():
    start_date = pytz.timezone("Australia/Melbourne").localize(datetime(2023, 7, 10, 12, 30, 45))
    result = get_rfc_3339_date_offset(start_date, 0)
    assert result == "2023-07-10T12:30:45+10:00"


def test_get_rfc_3339_date_offset_removes_microseconds():
    start_date = pytz.timezone("Australia/Melbourne").localize(datetime(2023, 7, 10, 12, 30, 45, 123456))
    result = get_rfc_3339_date_offset(start_date, 0)
    assert result == "2023-07-10T12:30:45+10:00"
    assert ".123456" not in result
