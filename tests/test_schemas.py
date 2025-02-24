from pathlib import Path

import pytest
import ujson
from up.classes import UpAPI
from up.utils import load_json, schema_validator

ACCOUNTS_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/accounts.schema.json")
TRANSACTIONS_SCHEMA = load_json(Path(__file__).parent.parent / "schemas/transactions.schema.json")

up_api = UpAPI()


@pytest.mark.schema
def test_accounts_schema():
    accounts_url = up_api.accounts_url
    response = up_api.get_endpoint_response(accounts_url)

    schema_validator(ujson.loads(response.text), ACCOUNTS_SCHEMA)


@pytest.mark.schema
def test_transactions_schema():
    transactions_url = up_api.transactions_url
    url_params = {
        "page[size]": 1,
        "filter[status]": "SETTLED",
    }

    response = up_api.get_endpoint_response(url=transactions_url, url_params=url_params)

    schema_validator(ujson.loads(response.text), TRANSACTIONS_SCHEMA)
