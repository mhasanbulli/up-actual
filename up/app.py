import datetime

from actual import get_transactions

from up.app_config import Settings
from up.classes import ActualSession, QueryParams, UpAPI
from up.logger import logger
from up.transactions import (
    create_transactions,
    get_account_transaction_urls,
    get_transactions_batch,
    reconcile_transactions,
)

logger.info("Starting up...")

up_api = UpAPI()
query_params = QueryParams(start_date=datetime.datetime(2025, 9, 1), days_offset=0, page_size=100)
actual_settings = Settings()  # type: ignore

actual_init = ActualSession(
    url=actual_settings.url.get_secret_value(),
    password=actual_settings.password.get_secret_value(),
    file=actual_settings.file,
    encryption_password=actual_settings.encryption_password.get_secret_value(),
)

actual_session = actual_init.get_actual_session()

if __name__ == "__main__":
    up_accounts = get_account_transaction_urls(up_api=up_api)
    for up_account in up_accounts:
        transactions_from_up = get_transactions_batch(
            up_api=up_api, query_params=query_params, account_name=up_account.name, url=up_account.url
        )

        if transactions_from_up.transactions:
            with actual_session as a:
                logger.info("Getting transactions from Actual...")

                transactions_from_actual = get_transactions(
                    a.session, account=transactions_from_up.account_name, start_date=query_params.start_date
                )

                already_imported_transactions = []
                new_transactions = []
                actual_financial_ids = {transaction.financial_id for transaction in transactions_from_actual}

                # Separate new, and already existing transactions. Existing transactions will be reconciled.
                # New transactions will be inserted.
                for transaction_from_up in transactions_from_up.transactions:
                    if transaction_from_up["id"] in actual_financial_ids:
                        already_imported_transactions.append(transaction_from_up)
                    else:
                        new_transactions.append(transaction_from_up)

                reconcile_transactions(
                    session=a.session,
                    account_name=transactions_from_up.account_name,
                    transactions=already_imported_transactions,
                    already_imported_transactions=already_imported_transactions,
                )

                create_transactions(
                    session=a.session, account_name=transactions_from_up.account_name, transactions=new_transactions
                )

                a.commit()

                up_account.next_url = transactions_from_up.next_url

                while up_account.next_url:
                    transactions_from_up = get_transactions_batch(
                        up_api=up_api, query_params=None, account_name=up_account.name, url=up_account.next_url
                    )

                    transactions_from_actual = get_transactions(
                        a.session, account=transactions_from_up.account_name, start_date=query_params.start_date
                    )

                    already_imported_transactions = []
                    new_transactions = []
                    actual_financial_ids = {transaction.financial_id for transaction in transactions_from_actual}

                    for transaction_from_up in transactions_from_up.transactions:
                        if transaction_from_up["id"] in actual_financial_ids:
                            already_imported_transactions.append(transaction_from_up)
                        else:
                            new_transactions.append(transaction_from_up)

                    reconcile_transactions(
                        session=a.session,
                        account_name=transactions_from_up.account_name,
                        transactions=already_imported_transactions,
                        already_imported_transactions=already_imported_transactions,
                    )

                    create_transactions(
                        session=a.session, account_name=transactions_from_up.account_name, transactions=new_transactions
                    )

                    a.commit()

                    up_account.next_url = transactions_from_up.next_url
