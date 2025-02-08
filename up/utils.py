import json
import os
from pathlib import Path
from urllib.parse import urlencode, urljoin

from jsonschema import ValidationError, validate

from up.logger import logger


def get_token() -> str:
    up_token = os.getenv("UP_TOKEN")

    if up_token is None:
        raise OSError("UP_TOKEN environment variable is not set.")
    return up_token


def load_json(file_path: Path) -> dict:
    with file_path.open(mode="r", encoding="utf-8") as file:
        return json.load(file)


def schema_validator(instance: dict, schema: dict) -> None:
    try:
        validate(instance=instance, schema=schema)
        logger.info("Validation passed \u2728")
    except ValidationError as e:
        raise ValidationError(f"Validation error: {e}") from e


def get_url(base_url: str, url_params: dict | None = None) -> str | bytes:
    params = {}

    if url_params is not None:
        for key, value in url_params.items():
            if isinstance(value, list):
                for item in value:
                    params[key] = item
            elif value is not None:
                params[key] = value

    encoded_params = urlencode(params)
    url = "?" + encoded_params if encoded_params != "" else ""

    return urljoin(base=base_url, url=url)
