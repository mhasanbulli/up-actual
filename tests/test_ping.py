import pytest
from unittest.mock import patch
from conftest import ping, HEADERS

def test_ping():
    mock_response = {
        "meta": {
            "id": "3b5d17a4-6778-48dc-ae7d-9f8aace2e2fc",
            "statusEmoji": "⚡️"
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        response = ping()

        mock_get.assert_called_once_with(url=f"API_URL/ping", headers=HEADERS)
        assert response == mock_response
