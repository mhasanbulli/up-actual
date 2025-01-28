import json
from pathlib import Path

import pytest
from up.classes import UpAPI
from up.utils import load_json, schema_validator

ACCOUNTS_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/accounts.schema.json")


@pytest.mark.schema
def test_accounts_schema():
    accounts_endpoint = UpAPI(endpoint="accounts")
    response = accounts_endpoint.get_endpoint_response()

    schema_validator(json.loads(response.text), ACCOUNTS_SCHEMA)
