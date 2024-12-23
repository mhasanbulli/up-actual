from unittest.mock import patch

from conftest import HEADERS, ping


def test_ping():
    mock_response = {"meta": {"id": "3b5d17a4-6778-48dc-ae7d-9f8aace2e2fc", "statusEmoji": "⚡️"}}

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        response = ping()

        mock_get.assert_called_once_with(url="API_URL/ping", headers=HEADERS, timeout=1)
        assert response == mock_response
