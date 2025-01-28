import json
from pathlib import Path

from up.classes import UpAPI
from up.logger import logger
from up.utils import load_json, schema_validator

logger.info("Starting up...")
RESPONSE_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/accounts.schema.json")


def get_accounts(response_schema: dict) -> dict:
    logger.info("Getting accounts...")

    accounts_endpoint = UpAPI(endpoint="accounts")
    response = accounts_endpoint.get_endpoint_response()

    schema_validator(json.loads(response.text), response_schema)

    return json.loads(response.text)


if __name__ == "__main__":
    get_accounts(RESPONSE_SCHEMA)
