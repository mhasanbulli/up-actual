from datetime import datetime
from decimal import Decimal
from json import JSONDecodeError

import ujson
from actual import Session, Transactions, create_transaction, get_transactions, reconcile_transaction
from actual.queries import get_ruleset
from requests import RequestException

from up.classes import AccountBatchTransactions, Actual, Categories, QueryParams, SimplifiedCategories, UpAccount, UpAPI
from up.logger import logger


def get_account_transaction_urls(up_api: UpAPI) -> list[UpAccount]:
    logger.info("Getting accounts...")

    url_accounts = up_api.accounts_url
    response = up_api.get_endpoint_response(url_accounts)
    response_json = ujson.loads(response.text)

    return [
        UpAccount(
            name=account["attributes"]["displayName"], url=account["relationships"]["transactions"]["links"]["related"]
        )
        for account in response_json["data"]
    ]


def get_transactions_batch(
    up_api: UpAPI, query_params: QueryParams | None, account_name: str, url: str
) -> AccountBatchTransactions:
    url_params = query_params.get_params() if query_params else None

    try:
        logger.info(f"Fetching transactions for {account_name}...")

        response = up_api.get_endpoint_response(url=url, url_params=url_params)
        response_json = ujson.loads(response.text)
        transactions = response_json["data"]
        next_url = response_json.get("links", {}).get("next")

    except (RequestException, JSONDecodeError, KeyError) as e:
        logger.error(f"Error fetching transactions: {e!s}")
        raise

    return AccountBatchTransactions(account_name=account_name, transactions=transactions, next_url=next_url)


def reconcile_transactions(
    session: Session, account_name: str, transactions: list, already_imported_transactions: list[Transactions]
) -> None:
    rule_set = get_ruleset(session)

    for transaction in transactions:
        category_data = transaction.get("relationships", {}).get("category", {}).get("data", {})
        category = Categories(category_data.get("id")) if category_data else None
        simplified_category = SimplifiedCategories.get_simplified_category_label(category_class=category)

        transaction_attributes = transaction.get("attributes")

        amount = (
            Decimal(transaction_attributes["amount"]["value"])
            + Decimal(transaction_attributes["roundUp"]["amount"]["value"])
            if transaction_attributes["roundUp"]
            else Decimal(transaction_attributes["amount"]["value"])
        )

        reconciled_transaction = reconcile_transaction(
            s=session,
            imported_id=transaction["id"],
            date=datetime.fromisoformat(transaction_attributes["createdAt"]).date(),
            account=account_name,
            payee=transaction_attributes["description"],
            imported_payee=transaction_attributes["rawText"],
            notes=transaction_attributes["message"],
            amount=amount,
            category=simplified_category,
            cleared=bool(transaction_attributes["status"] == "SETTLED"),
            already_matched=already_imported_transactions,
            update_existing=True,
        )

        rule_set.run(reconciled_transaction)


def create_transactions(
    session: Session,
    account_name: str,
    transactions: list,
) -> None:
    rule_set = get_ruleset(session)

    for transaction in transactions:
        category_data = transaction.get("relationships", {}).get("category", {}).get("data", {})
        category = Categories(category_data.get("id")) if category_data else None
        simplified_category = SimplifiedCategories.get_simplified_category_label(category_class=category)

        transaction_attributes = transaction.get("attributes")

        amount = (
            Decimal(transaction_attributes["amount"]["value"])
            + Decimal(transaction_attributes["roundUp"]["amount"]["value"])
            if transaction_attributes["roundUp"]
            else Decimal(transaction_attributes["amount"]["value"])
        )

        created_transaction = create_transaction(
            s=session,
            imported_id=transaction["id"],
            date=datetime.fromisoformat(transaction_attributes["createdAt"]).date(),
            account=account_name,
            payee=transaction_attributes["description"],
            imported_payee=transaction_attributes["rawText"],
            notes=transaction_attributes["message"],
            amount=amount,
            category=simplified_category,
            cleared=bool(transaction_attributes["status"] == "SETTLED"),
        )

        rule_set.run(created_transaction)


def classify_transactions(up_transactions: list, actual_financial_ids: set[str]) -> tuple[list, list]:
    already_imported = []
    new = []
    for transaction in up_transactions:
        if transaction["id"] in actual_financial_ids:
            already_imported.append(transaction)
        else:
            new.append(transaction)
    return already_imported, new


def process_batch(session: Session, account_name: str, up_transactions: list, start_date: datetime) -> None:
    logger.info("Getting transactions from Actual...")
    transactions_from_actual = get_transactions(session, account=account_name, start_date=start_date)
    actual_financial_ids = {
        transaction.financial_id for transaction in transactions_from_actual if transaction.financial_id
    }

    # This should filter out card check transactions that gets deleted after a couple of days.
    # For now, this happens with only Myki. If other's starts to do this, we will need to find
    # a better way to do this.
    filtered_up_transactions = [
        transaction
        for transaction in up_transactions
        if not (
            (transaction.get("attributes") or {}).get("status") == "HELD"
            and (transaction.get("attributes") or {}).get("description") == "Myki"
            and ((transaction.get("attributes") or {}).get("amount") or {}).get("value") == "-1.00"
        )
    ]

    already_imported, new = classify_transactions(filtered_up_transactions, actual_financial_ids)

    reconcile_transactions(
        session=session,
        account_name=account_name,
        transactions=already_imported,
        already_imported_transactions=already_imported,
    )
    create_transactions(session=session, account_name=account_name, transactions=new)


def reconcile_accounts(
    accounts: list[UpAccount], up_api: UpAPI, actual_session: Actual, query_params: QueryParams
) -> None:
    with actual_session as a:
        for up_account in accounts:
            url = up_account.url
            params = query_params

            while url:
                batch = get_transactions_batch(
                    up_api=up_api, query_params=params, account_name=up_account.name, url=up_account.url
                )

                if batch.transactions:
                    process_batch(a.session, batch.account_name, batch.transactions, query_params.start_date)
                    a.commit()

                    url = batch.next_url
                    params = None
