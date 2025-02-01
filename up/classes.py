from dataclasses import dataclass
from urllib.parse import urlencode, urljoin

import requests
from requests import Response

from up.utils import get_token


@dataclass
class UpAPI:
    endpoint: str

    @property
    def up_api_url(self) -> str:
        return "https://api.up.com.au/api/v1"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {get_token()}"}

    def get_url(self, url_params: dict | None = None) -> str | bytes:
        if url_params is None and not self.endpoint:
            return self.up_api_url

        base_url = f"{self.up_api_url}/{self.endpoint}"

        params = {}

        if url_params is not None:
            for key, value in url_params.items():
                if isinstance(value, list):
                    for item in value:
                        params[key] = item
                elif value is not None:
                    params[key] = value

        encoded_params = urlencode(params)
        url = "?" + encoded_params if encoded_params != "" else ""

        return urljoin(base=base_url, url=url)

    def get_endpoint_response(self, url_params: dict | None = None) -> Response:
        """
        For a given `endpoint`, it returns the response from the Up API.
        """
        url = self.get_url(url_params)
        response = requests.get(url=url, headers=self.headers, timeout=1)

        return response
