import requests


API_VERSION = 1
API_URL = f"https://api.up.com.au/api/v{API_VERSION}"
UP_TOKEN = "TOKEN"
HEADERS = {
    "Authorization": f"Bearer {UP_TOKEN}"
}

def ping() -> dict:
    response = requests.get(url=f"API_URL/ping", headers=HEADERS)
    return response.json()
