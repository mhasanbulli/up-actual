from dataclasses import dataclass

import requests
from actual import Actual
from requests import Response

from up.utils import get_rfc_3339_date, get_token, get_url


@dataclass
class UpAPI:
    @property
    def up_api_url(self) -> str:
        return "https://api.up.com.au/api/v1"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {get_token()}"}

    @property
    def accounts_url(self) -> str:
        return f"{self.up_api_url}/accounts"

    @property
    def ping_url(self) -> str:
        return f"{self.up_api_url}/util/ping"

    @property
    def transactions_url(self) -> str:
        return f"{self.up_api_url}/transactions"

    def get_endpoint_response(self, url: str, url_params: dict | None = None) -> Response:
        url = get_url(url, url_params)
        response = requests.get(url=url, headers=self.headers, timeout=1)

        return response


@dataclass
class UpAccount:
    name: str
    url: str


@dataclass
class AccountTransactions:
    account_name: str
    transactions: list


@dataclass
class QueryParams:
    page_size: int = 10
    status: str = "SETTLED"
    days: int = 2

    def get_params(self) -> dict:
        return {
            "page[size]": self.page_size,
            "filter[status]": self.status,
            "filter[since]": get_rfc_3339_date(self.days),
        }


@dataclass
class ActualSession:
    url: str
    password: str
    file: str
    encryption_password: str

    def get_actual_session(self) -> Actual:
        return Actual(
            base_url=self.url, password=self.password, file=self.file, encryption_password=self.encryption_password
        )
