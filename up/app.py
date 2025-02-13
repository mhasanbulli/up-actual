import json
from json import JSONDecodeError

from requests import RequestException

from up.classes import AccountTransactions, QueryParams, UpAccount, UpAPI
from up.logger import logger

up_api = UpAPI()
query_params = QueryParams()

logger.info("Starting up...")


def get_account_transaction_urls() -> list[UpAccount]:
    logger.info("Getting accounts...")

    url_accounts = up_api.accounts_url
    response = up_api.get_endpoint_response(url_accounts)
    response_json = json.loads(response.text)

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
            response_json = json.loads(response.text)

            transactions.extend(response_json["data"])
            next_url = response_json.get("links", {}).get("next")

    except (RequestException, JSONDecodeError, KeyError) as e:
        logger.error(f"Error fetching transactions: {e!s}")
        raise

    return AccountTransactions(account_name=account.name, transactions=transactions)


if __name__ == "__main__":
    up_accounts = get_account_transaction_urls()
    for up_account in up_accounts:
        account_transactions = get_transactions(up_account)
