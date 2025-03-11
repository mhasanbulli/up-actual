from datetime import datetime
from decimal import Decimal
from json import JSONDecodeError

import ujson
from actual import Actual, reconcile_transaction
from actual.queries import get_ruleset
from requests import RequestException

from up.classes import (
    AccountBatchTransactions,
    Categories,
    QueryParams,
    SimplifiedCategories,
    UpAccount,
    UpAPI,
)
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


def reconcile_transactions(actual_session: Actual, transactions: AccountBatchTransactions) -> None:
    logger.info(f"Reconciling transactions for {transactions.account_name}...")

    with actual_session as a:
        rule_set = get_ruleset(a.session)

        for transaction in transactions.transactions:
            category_data = transaction.get("relationships", {}).get("category", {}).get("data", {})
            category = Categories(category_data.get("id")) if category_data else None
            simplified_category = SimplifiedCategories.get_simplified_category_label(category_class=category)

            transaction = reconcile_transaction(
                a.session,
                date=datetime.fromisoformat(transaction["attributes"]["createdAt"]).date(),
                account=transactions.account_name,
                payee=transaction["attributes"]["description"],
                imported_payee=transaction["attributes"]["rawText"],
                notes=transaction["attributes"]["message"],
                amount=Decimal(transaction["attributes"]["amount"]["value"]),
                imported_id=transaction["id"],
                category=simplified_category,
                update_existing=True,
                cleared=bool(transaction["attributes"]["status"] == "SETTLED"),
            )
            rule_set.run(transaction)

        a.commit()
