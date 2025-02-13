import pytest
from up.classes import UpAPI


def test_dummy_test():
    assert 1 == 1


@pytest.mark.integration
def test_ping():
    up_api = UpAPI()
    ping_url = up_api.ping_url
    response = up_api.get_endpoint_response(ping_url)

    assert response.status_code == 200
