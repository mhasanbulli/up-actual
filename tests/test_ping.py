import pytest
from up.classes import UpAPI


def test_dummy_test():
    assert 1 == 1


@pytest.mark.integration
def test_ping():
    ping_endpoint = UpAPI(endpoint="util/ping")
    response = ping_endpoint.get_endpoint_response()

    assert response.status_code == 200
