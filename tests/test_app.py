import pytest
from up.app_config import Settings


def test_get_settings(mock_actual_env_vars: pytest.MonkeyPatch):  # noqa: ARG001
    settings = Settings()  # type: ignore

    assert settings.url.get_secret_value() == "https://actual.com"
    assert settings.password.get_secret_value() == "password"
    assert settings.encryption_password.get_secret_value() == "password"
    assert settings.file == "file"
