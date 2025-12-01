import datetime
from typing import Annotated

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

app = typer.Typer(
    name="up-actual",
    help="Synchronise transactions from Up Banking to Actual Budget",
    add_completion=False,
)


@app.command()
def reconcile(
    start_date: Annotated[
        str | None,
        typer.Option(
            "--start-date",
            help="Start date in ISO format (YYYY-MM-DD). If provided, overrides --days-back.",
        ),
    ] = None,
    days_back: Annotated[
        int,
        typer.Option(
            "--days-back",
            help="Number of days back from today to sync transactions (default: 30)",
        ),
    ] = 30,
    page_size: Annotated[
        int,
        typer.Option(
            "--page-size",
            help="Number of transactions to fetch per API request (default: 100, max: 100)",
        ),
    ] = 100,
) -> None:
    """
    Reconcile transactions from Up Banking to Actual Budget.

    This command fetches transactions from your Up Banking accounts and syncs them
    to Actual Budget. It will create new transactions and update existing ones.

    Examples:

        # Sync transactions from the last 30 days (default)
        $ up-actual reconcile

        # Sync transactions from the last 90 days
        $ up-actual reconcile --days-back 90

        # Sync transactions from a specific date
        $ up-actual reconcile --start-date 2025-01-01

        # Customize the page size
        $ up-actual reconcile --page-size 50
    """
    up_api = UpAPI()

    # Determine the start date
    if start_date:
        try:
            parsed_date = datetime.datetime.fromisoformat(start_date)
            logger.info(f"Using provided start date: {start_date}")
        except ValueError as e:
            logger.error(f"Invalid date format: {start_date}. Expected format: YYYY-MM-DD")
            raise typer.Exit(code=1) from e
    else:
        parsed_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        logger.info(f"Syncing transactions from the last {days_back} days")

    query_params = QueryParams(start_date=parsed_date, days_offset=0, page_size=page_size)
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
