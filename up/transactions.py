from datetime import datetime
from decimal import Decimal
from json import JSONDecodeError

import ujson
from actual import reconcile_transaction
from requests import RequestException

from up.app import actual, query_params, up_api
from up.classes import AccountTransactions, Categories, SimplifiedCategories, UpAccount
from up.logger import logger


def get_account_transaction_urls() -> list[UpAccount]:
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


def get_transactions(account: UpAccount) -> AccountTransactions:
    transactions = []
    next_url = account.url
    url_params = query_params.get_params()

    try:
        while next_url:
            response = up_api.get_endpoint_response(url=next_url, url_params=url_params)
            response_json = ujson.loads(response.text)

            transactions.extend(response_json["data"])
            next_url = response_json.get("links", {}).get("next")

    except (RequestException, JSONDecodeError, KeyError) as e:
        logger.error(f"Error fetching transactions: {e!s}")
        raise

    return AccountTransactions(account_name=account.name, transactions=transactions)


def reconcile_transactions(transactions: AccountTransactions) -> None:
    logger.info(f"Reconciling transactions for {transactions.account_name}...")

    with actual as a:
        for transaction in transactions.transactions:
            category_data = transaction.get("relationships", {}).get("category", {}).get("data", {})
            category = Categories(category_data.get("id")) if category_data else None
            simplified_category = SimplifiedCategories.get_simplified_category_label(category_class=category)

            reconcile_transaction(
                a.session,
                date=datetime.fromisoformat(transaction["attributes"]["createdAt"]).date(),
                account=transactions.account_name,
                payee=transaction["attributes"]["description"],
                notes=transaction["attributes"]["message"],
                amount=Decimal(transaction["attributes"]["amount"]["value"]),
                imported_id=transaction["id"],
                category=simplified_category,
                update_existing=True,
                cleared=True,
            )
        a.commit()
