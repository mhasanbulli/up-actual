from dataclasses import dataclass

import requests
from requests import Response

from up.utils import get_token, get_url


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
