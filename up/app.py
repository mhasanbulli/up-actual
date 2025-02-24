from up.app_config import Settings
from up.classes import ActualSession, QueryParams, UpAPI
from up.logger import logger

logger.info("Starting up...")

up_api = UpAPI()
query_params = QueryParams()
actual_settings = Settings()  # type: ignore

actual_session = ActualSession(
    url=actual_settings.url.get_secret_value(),
    password=actual_settings.password.get_secret_value(),
    file=actual_settings.file,
    encryption_password=actual_settings.encryption_password.get_secret_value(),
)

actual = actual_session.get_actual_session()

if __name__ == "__main__":
    from up.transactions import get_account_transaction_urls, get_transactions, reconcile_transactions

    up_accounts = get_account_transaction_urls()
    for up_account in up_accounts:
        account_transactions = get_transactions(up_account)
        reconcile_transactions(account_transactions)
