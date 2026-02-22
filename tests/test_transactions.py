from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import ujson
from requests import RequestException
from up.classes import AccountBatchTransactions, QueryParams, UpAccount, UpAPI
from up.transactions import (
    classify_transactions,
    create_transactions,
    get_account_transaction_urls,
    get_transactions_batch,
    process_batch,
    reconcile_accounts,
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
        "relationships": {"category": {"data": {"id": "groceries"}}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
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
        "relationships": {"category": {"data": {"id": "booze"}}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.create_transaction", return_value="created_txn") as mock_create,
    ):
        create_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=[mock_transaction],
        )
        mock_create.assert_called_once()
        mock_rule_set.run.assert_called_once_with("created_txn")


def test_get_transactions_batch_no_next_page():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.get_endpoint_response.return_value.text = ujson.dumps(
        {"data": [{"id": "txn1"}], "links": {}}  # No "next" key in links
    )

    query_params = MagicMock(spec=QueryParams)
    query_params.get_params.return_value = {"page[size]": 10}

    result = get_transactions_batch(
        up_api=mock_api,
        query_params=query_params,
        account_name="Test Account",
        url="https://api.up.com.au/accounts/1/transactions",
    )

    assert result.next_url is None


def test_get_transactions_batch_empty_list():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.get_endpoint_response.return_value.text = ujson.dumps({"data": [], "links": {}})

    query_params = MagicMock(spec=QueryParams)
    query_params.get_params.return_value = {"page[size]": 10}

    result = get_transactions_batch(
        up_api=mock_api,
        query_params=query_params,
        account_name="Test Account",
        url="https://api.up.com.au/accounts/1/transactions",
    )

    assert len(result.transactions) == 0
    assert result.account_name == "Test Account"


def test_get_transactions_batch_with_no_query_params():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.get_endpoint_response.return_value.text = ujson.dumps({"data": [{"id": "txn1"}], "links": {}})

    result = get_transactions_batch(
        up_api=mock_api,
        query_params=None,
        account_name="Test Account",
        url="https://api.up.com.au/accounts/1/transactions",
    )

    mock_api.get_endpoint_response.assert_called_once_with(
        url="https://api.up.com.au/accounts/1/transactions", url_params=None
    )
    assert len(result.transactions) == 1


def test_get_transactions_batch_request_exception():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.get_endpoint_response.side_effect = RequestException("Network error")

    query_params = MagicMock(spec=QueryParams)
    query_params.get_params.return_value = {"page[size]": 10}

    with pytest.raises(RequestException):
        get_transactions_batch(
            up_api=mock_api,
            query_params=query_params,
            account_name="Test Account",
            url="https://api.up.com.au/accounts/1/transactions",
        )


def test_get_account_transaction_urls_empty_accounts():
    mock_api = MagicMock(spec=UpAPI)
    mock_api.accounts_url = "https://api.up.com.au/accounts"
    mock_api.get_endpoint_response.return_value.text = ujson.dumps({"data": []})

    result = get_account_transaction_urls(mock_api)

    assert len(result) == 0


def test_reconcile_transactions_without_category():
    mock_session = MagicMock()
    mock_rule_set = MagicMock()
    mock_transaction = {
        "id": "txn3",
        "attributes": {
            "createdAt": "2025-06-10T12:00:00Z",
            "description": "Test Payee",
            "rawText": "Raw Payee",
            "message": None,
            "amount": {"value": "100.00"},
            "roundUp": None,
            "status": "HELD",
        },
        "relationships": {"category": {"data": None}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.reconcile_transaction", return_value="reconciled_txn") as mock_reconcile,
    ):
        reconcile_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=[mock_transaction],
            already_imported_transactions=[],
        )
        mock_reconcile.assert_called_once()

        call_args = mock_reconcile.call_args
        assert call_args[1]["cleared"] is False
        assert call_args[1]["category"] is None


def test_create_transactions_without_round_up():
    mock_session = MagicMock()
    mock_rule_set = MagicMock()
    mock_transaction = {
        "id": "txn4",
        "attributes": {
            "createdAt": "2025-06-10T12:00:00Z",
            "description": "Test Payee",
            "rawText": "Raw Payee",
            "message": "Test",
            "amount": {"value": "75.50"},
            "roundUp": None,
            "status": "SETTLED",
        },
        "relationships": {"category": {"data": {"id": "groceries"}}},
    }
    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.create_transaction", return_value="created_txn") as mock_create,
    ):
        create_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=[mock_transaction],
        )
        mock_create.assert_called_once()

        call_args = mock_create.call_args
        from decimal import Decimal

        assert call_args[1]["amount"] == Decimal("75.50")


def test_create_transactions_multiple():
    mock_session = MagicMock()
    mock_rule_set = MagicMock()
    category_ids = ["groceries", "booze", "fuel"]
    mock_transactions = [
        {
            "id": f"txn{i}",
            "attributes": {
                "createdAt": "2025-06-10T12:00:00Z",
                "description": f"Payee {i}",
                "rawText": f"Raw {i}",
                "message": None,
                "amount": {"value": f"{i * 10}.00"},
                "roundUp": None,
                "status": "SETTLED",
            },
            "relationships": {"category": {"data": {"id": category_ids[i - 1]}}},
        }
        for i in range(1, 4)
    ]

    with (
        patch("up.transactions.get_ruleset", return_value=mock_rule_set),
        patch("up.transactions.create_transaction", return_value="created_txn") as mock_create,
    ):
        create_transactions(
            session=mock_session,
            account_name="Test Account",
            transactions=mock_transactions,
        )

        assert mock_create.call_count == 3
        assert mock_rule_set.run.call_count == 3


def test_reconcile_accounts_with_empty_accounts():
    mock_up_api = MagicMock()
    mock_actual_session = MagicMock()
    mock_query_params = MagicMock()

    reconcile_accounts(
        accounts=[], up_api=mock_up_api, actual_session=mock_actual_session, query_params=mock_query_params
    )


def test_reconcile_accounts_with_pagination():
    mock_up_api = MagicMock()
    mock_actual_session = MagicMock()
    mock_query_params = MagicMock()
    mock_query_params.start_date = "2025-01-01"

    mock_account = UpAccount(name="Test Account", url="https://api.example.com/transactions")

    # First batch
    first_batch = {
        "id": "txn1",
        "attributes": {
            "createdAt": "2025-06-10T12:00:00Z",
            "description": "Test",
            "rawText": "Raw",
            "message": None,
            "amount": {"value": "100.00"},
            "roundUp": None,
            "status": "SETTLED",
        },
        "relationships": {"category": {"data": {"id": "cat1"}}},
    }

    # Second batch
    second_batch = {
        "id": "txn2",
        "attributes": {
            "createdAt": "2025-06-11T12:00:00Z",
            "description": "Test 2",
            "rawText": "Raw 2",
            "message": None,
            "amount": {"value": "50.00"},
            "roundUp": None,
            "status": "SETTLED",
        },
        "relationships": {"category": {"data": {"id": "cat2"}}},
    }

    with (
        patch("up.transactions.get_transactions_batch") as mock_get_batch,
        patch("up.transactions.get_transactions") as mock_get_actual_txns,
        patch("up.transactions.reconcile_transactions") as mock_reconcile,
        patch("up.transactions.create_transactions") as mock_create,
    ):
        # Mock get_transactions_batch to return first batch, then second batch, then no next_url
        mock_get_batch.side_effect = [
            AccountBatchTransactions(
                account_name="Test Account", transactions=[first_batch], next_url="https://api.example.com/next"
            ),
            AccountBatchTransactions(account_name="Test Account", transactions=[second_batch], next_url=None),
        ]

        # Mock Actual Budget transactions
        mock_get_actual_txns.return_value = []

        # Mock Actual session context manager
        mock_session_context = MagicMock()
        mock_actual_session.__enter__.return_value = mock_session_context
        mock_actual_session.__exit__.return_value = None

        reconcile_accounts(
            accounts=[mock_account],
            up_api=mock_up_api,
            actual_session=mock_actual_session,
            query_params=mock_query_params,
        )

        # Should be called twice - once for first batch, once for second batch
        assert mock_get_batch.call_count == 2
        # Should create transactions twice (once per batch)
        assert mock_create.call_count == 2
        # Should reconcile twice (once per batch, though with empty already_imported)
        assert mock_reconcile.call_count == 2


def test_classify_transactions_mixed():
    up_txns = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    actual_ids = {"a", "c"}
    already, new = classify_transactions(up_txns, actual_ids)
    assert already == [{"id": "a"}, {"id": "c"}]
    assert new == [{"id": "b"}]


def test_classify_transactions_all_existing():
    up_txns = [{"id": "a"}, {"id": "b"}]
    actual_ids = {"a", "b"}
    already, new = classify_transactions(up_txns, actual_ids)
    assert already == [{"id": "a"}, {"id": "b"}]
    assert new == []


def test_classify_transactions_all_new():
    up_txns = [{"id": "x"}, {"id": "y"}]
    actual_ids = {"a", "b"}
    already, new = classify_transactions(up_txns, actual_ids)
    assert already == []
    assert new == [{"id": "x"}, {"id": "y"}]


def test_classify_transactions_empty():
    already, new = classify_transactions([], {"a"})
    assert already == []
    assert new == []


@patch("up.transactions.create_transactions")
@patch("up.transactions.reconcile_transactions")
@patch("up.transactions.get_transactions")
def test_process_batch_splits_and_dispatches(
    mock_get_txns: MagicMock, mock_reconcile: MagicMock, mock_create: MagicMock
):
    mock_actual_txn = MagicMock()
    mock_actual_txn.financial_id = "existing-1"
    mock_get_txns.return_value = [mock_actual_txn]

    up_transactions = [{"id": "existing-1"}, {"id": "new-1"}]
    session = MagicMock()
    start_date = datetime(2025, 1, 1)

    process_batch(session, "Spending", up_transactions, start_date)

    mock_get_txns.assert_called_once_with(session, account="Spending", start_date=start_date)
    mock_reconcile.assert_called_once_with(
        session=session,
        account_name="Spending",
        transactions=[{"id": "existing-1"}],
        already_imported_transactions=[{"id": "existing-1"}],
    )
    mock_create.assert_called_once_with(session=session, account_name="Spending", transactions=[{"id": "new-1"}])


@patch("up.transactions.create_transactions")
@patch("up.transactions.reconcile_transactions")
@patch("up.transactions.get_transactions")
def test_process_batch_all_new(mock_get_txns: MagicMock, mock_reconcile: MagicMock, mock_create: MagicMock):
    mock_get_txns.return_value = []

    up_transactions = [{"id": "new-1"}, {"id": "new-2"}]
    session = MagicMock()

    process_batch(session, "Spending", up_transactions, datetime(2025, 1, 1))

    mock_reconcile.assert_called_once_with(
        session=session,
        account_name="Spending",
        transactions=[],
        already_imported_transactions=[],
    )
    mock_create.assert_called_once_with(
        session=session, account_name="Spending", transactions=[{"id": "new-1"}, {"id": "new-2"}]
    )


@patch("up.transactions.create_transactions")
@patch("up.transactions.reconcile_transactions")
@patch("up.transactions.get_transactions")
def test_process_batch_all_existing(mock_get_txns: MagicMock, mock_reconcile: MagicMock, mock_create: MagicMock):
    mock_actual_1 = MagicMock()
    mock_actual_1.financial_id = "a"
    mock_actual_2 = MagicMock()
    mock_actual_2.financial_id = "b"
    mock_get_txns.return_value = [mock_actual_1, mock_actual_2]

    up_transactions = [{"id": "a"}, {"id": "b"}]
    session = MagicMock()

    process_batch(session, "Spending", up_transactions, datetime(2025, 1, 1))

    mock_reconcile.assert_called_once_with(
        session=session,
        account_name="Spending",
        transactions=[{"id": "a"}, {"id": "b"}],
        already_imported_transactions=[{"id": "a"}, {"id": "b"}],
    )
    mock_create.assert_called_once_with(session=session, account_name="Spending", transactions=[])
