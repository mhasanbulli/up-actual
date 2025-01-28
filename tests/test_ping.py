import pytest
from up.classes import UpAPI


@pytest.mark.integration
def test_ping():
    ping_endpoint = UpAPI(endpoint="util/ping")
    response = ping_endpoint.get_endpoint_response()

    assert response.status_code == 200
