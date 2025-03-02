import datetime

from up.app_config import Settings
from up.classes import ActualSession, QueryParams, UpAPI
from up.logger import logger
from up.transactions import get_account_transaction_urls, get_transactions_batch, reconcile_transactions

logger.info("Starting up...")

up_api = UpAPI()
query_params = QueryParams(start_date=datetime.datetime(2025, 2, 1), days_offset=0, page_size=100)
actual_settings = Settings()  # type: ignore

actual_init = ActualSession(
    url=actual_settings.url.get_secret_value(),
    password=actual_settings.password.get_secret_value(),
    file=actual_settings.file,
    encryption_password=actual_settings.encryption_password.get_secret_value(),
)

actual = actual_init.get_actual_session()

if __name__ == "__main__":
    up_accounts = get_account_transaction_urls(up_api=up_api)
    for up_account in up_accounts:
        account_transactions = get_transactions_batch(
            up_api=up_api, query_params=query_params, account_name=up_account.name, url=up_account.url
        )

        reconcile_transactions(actual_session=actual, transactions=account_transactions)
        up_account.next_url = account_transactions.next_url

        while up_account.next_url:
            account_transactions = get_transactions_batch(
                up_api=up_api, query_params=None, account_name=up_account.name, url=up_account.next_url
            )

            reconcile_transactions(actual_session=actual, transactions=account_transactions)
            up_account.next_url = account_transactions.next_url
