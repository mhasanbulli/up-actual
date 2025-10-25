import datetime

import typer
from dotenv import load_dotenv

from up.classes import ActualSession, QueryParams, UpAPI
from up.config import Settings
from up.logger import logger
from up.transactions import (
    get_account_transaction_urls,
    reconcile_accounts,
)

logger.info("Starting up...")

if load_dotenv():
    logger.info("Loaded .env successfully...")
else:
    print("No .env file found...")

app = typer.Typer()


@app.command()
def reconcile() -> None:
    up_api = UpAPI()
    query_params = QueryParams(start_date=datetime.datetime(2025, 10, 1), days_offset=0, page_size=100)
    actual_settings = Settings()  # type: ignore

    actual_init = ActualSession(
        url=actual_settings.url.get_secret_value(),
        password=actual_settings.password.get_secret_value(),
        file=actual_settings.file,
        encryption_password=actual_settings.encryption_password.get_secret_value(),
    )

    actual_session = actual_init.get_actual_session()

    up_accounts = get_account_transaction_urls(up_api=up_api)
    reconcile_accounts(up_accounts, up_api, actual_session, query_params)


if __name__ == "__main__":
    app()
