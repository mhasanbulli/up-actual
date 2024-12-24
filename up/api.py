import requests
from dataclasses import dataclass
from up.utils import get_token


@dataclass
class UpAPI:
    endpoint: str

    @property
    def API_VERSION(self) -> int:
        return 1

    @property
    def API_URL(self) -> str:
        return f"https://api.up.com.au/api/v{self.API_VERSION}"

    @property
    def HEADERS(self) -> dict:
        return {"Authorization": f"Bearer {get_token()}"}

    def get_url(self) -> str:
        return f"{self.API_URL}/{self.endpoint}"

    def get_endpoint_response(self) -> dict:
        """
        For a given `endpoint`, it returns the response from the Up API.
        """
        url = self.get_url()
        response = requests.get(url=url, headers=self.HEADERS, timeout=1)

        return response.json()
