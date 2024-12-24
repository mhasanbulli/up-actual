from unittest.mock import patch

from up.api import UpAPI


def test_ping(monkeypatch):
    monkeypatch.setenv("UP_TOKEN", "test_token")
    
    ping_endpoint = UpAPI(endpoint="ping")
    mock_response = {"meta": {"id": "3b5d17a4-6778-48dc-ae7d-9f8aace2e2fc", "statusEmoji": "⚡️"}}

    with patch.object(ping_endpoint, "get_endpoint_response", return_value=mock_response) as mock_get:
        response = ping_endpoint.get_endpoint_response()

        mock_get.assert_called_once_with()
        assert response == mock_response
