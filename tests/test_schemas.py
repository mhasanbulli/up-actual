import json
from pathlib import Path

import pytest
from up.classes import UpAPI
from up.utils import load_json, schema_validator

ACCOUNTS_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/accounts.schema.json")
TRANSACTIONS_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/transactions.schema.json")


@pytest.mark.schema
def test_accounts_schema():
    accounts_endpoint = UpAPI(endpoint="accounts")
    response = accounts_endpoint.get_endpoint_response()

    schema_validator(json.loads(response.text), ACCOUNTS_SCHEMA)


@pytest.mark.schema
def test_transactions_schema():
    transactions_endpoint = UpAPI(endpoint="transactions")
    url_params = {
        "page[size]": 1,
    }

    response = transactions_endpoint.get_endpoint_response(url_params=url_params)

    schema_validator(json.loads(response.text), TRANSACTIONS_SCHEMA)
