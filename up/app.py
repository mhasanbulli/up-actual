import json

from json import JSONDecodeError
from requests import RequestException

from up.classes import UpAPI
from up.logger import logger

PAGE_SIZE: int = 100
up_api = UpAPI()

logger.info("Starting up...")


def get_account_transaction_urls() -> list[str]:
    logger.info("Getting accounts...")

    url_accounts = up_api.accounts_url
    response = up_api.get_endpoint_response(url_accounts)
    response_json = json.loads(response.text)

    return [url["relationships"]["transactions"]["links"]["related"] for url in response_json["data"]]


def get_transactions(url: str) -> list:
    transactions = []
    next_url = url
    url_params = {"page[size]": PAGE_SIZE}

    try:
        while next_url:
            response = up_api.get_endpoint_response(url=next_url, url_params=url_params)
            response_json = json.loads(response.text)

            transactions.extend(response_json["data"])
            next_url = response_json.get("links", {}).get("next")

    except (RequestException, JSONDecodeError, KeyError) as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise

    return transactions



if __name__ == "__main__":
    account_urls = get_account_transaction_urls()
    get_transactions(account_urls[0])

