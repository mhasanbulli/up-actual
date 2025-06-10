from unittest.mock import MagicMock, patch

import ujson
from up.classes import AccountBatchTransactions, QueryParams, UpAccount, UpAPI
from up.transactions import (
    create_transactions,
    get_account_transaction_urls,
    get_transactions_batch,
    reconcile_transactions,
)


def test_get_account_transaction_urls():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.accounts_url = "https://api.up.com.au/accounts"
    mock_api.get_endpoint_response.return_value.text = ujson.dumps(
        {
            "data": [
                {
                    "attributes": {"displayName": "Account 1"},
                    "relationships": {
                        "transactions": {"links": {"related": "https://api.up.com.au/accounts/1/transactions"}}
                    },
                },
                {
                    "attributes": {"displayName": "Account 2"},
                    "relationships": {
                        "transactions": {"links": {"related": "https://api.up.com.au/accounts/2/transactions"}}
                    },
                },
            ]
        }
    )

    result = get_account_transaction_urls(mock_api)

    assert len(result) == 2
    assert result[0] == UpAccount(name="Account 1", url="https://api.up.com.au/accounts/1/transactions")
    assert result[1] == UpAccount(name="Account 2", url="https://api.up.com.au/accounts/2/transactions")


def test_get_transactions_batch():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.get_endpoint_response.return_value.text = ujson.dumps(
        {"data": [{"id": "txn1"}, {"id": "txn2"}], "links": {"next": "https://api.up.com.au/next-page"}}
    )

    query_params = MagicMock(spec=QueryParams)
    query_params.get_params.return_value = {"page[size]": 10}

    result = get_transactions_batch(
        up_api=mock_api,
        query_params=query_params,
        account_name="Test Account",
        url="https://api.up.com.au/accounts/1/transactions",
    )

    assert isinstance(result, AccountBatchTransactions)
    assert result.account_name == "Test Account"
    assert len(result.transactions) == 2
    assert result.next_url == "https://api.up.com.au/next-page"


def test_reconcile_transactions():
    mock_session = MagicMock()
    mock_rule_set = MagicMock()
    mock_transaction = {
        "id": "txn1",
        "attributes": {
            "createdAt": "2025-06-10T12:00:00Z",
            "description": "Test Payee",
            "rawText": "Raw Payee",
            "message": "Test Message",
            "amount": {"value": "100.00"},
            "roundUp": None,
            "status": "SETTLED",
        },
        "relationships": {"category": {"data": {"id": "cat1"}}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.Categories", return_value="cat1"),
        patch("up.transactions.SimplifiedCategories.get_simplified_category_label", return_value="SimpleCat"),
        patch("up.transactions.reconcile_transaction", return_value="reconciled_txn") as mock_reconcile,
    ):
        reconcile_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=[mock_transaction],
            already_imported_transactions=[],
        )
        mock_reconcile.assert_called_once()
        mock_rule_set.run.assert_called_once_with("reconciled_txn")


def test_create_transactions():
    mock_session = MagicMock()
    mock_rule_set = MagicMock()
    mock_transaction = {
        "id": "txn2",
        "attributes": {
            "createdAt": "2025-06-10T12:00:00Z",
            "description": "Test Payee",
            "rawText": "Raw Payee",
            "message": "Test Message",
            "amount": {"value": "50.00"},
            "roundUp": {"amount": {"value": "5.00"}},
            "status": "SETTLED",
        },
        "relationships": {"category": {"data": {"id": "cat2"}}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.Categories", return_value="cat2"),
        patch("up.transactions.SimplifiedCategories.get_simplified_category_label", return_value="SimpleCat"),
        patch("up.transactions.create_transaction", return_value="created_txn") as mock_create,
    ):
        create_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=[mock_transaction],
        )
        mock_create.assert_called_once()
        mock_rule_set.run.assert_called_once_with("created_txn")
