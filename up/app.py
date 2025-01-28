import json

from up.classes import UpAPI
from up.logger import logger

logger.info("Starting up...")


def get_accounts() -> dict:
    logger.info("Getting accounts...")

    accounts_endpoint = UpAPI(endpoint="accounts")
    response = accounts_endpoint.get_endpoint_response()

    return json.loads(response.text)


if __name__ == "__main__":
    get_accounts()
