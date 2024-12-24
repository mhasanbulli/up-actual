from dataclasses import dataclass

import requests

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

    def get_url(self) -> str:
        return f"{self.up_api_url}/{self.endpoint}"

    def get_endpoint_response(self) -> dict:
        """
        For a given `endpoint`, it returns the response from the Up API.
        """
        url = self.get_url()
        response = requests.get(url=url, headers=self.headers, timeout=1)

        return response.json()
