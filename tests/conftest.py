import pytest


@pytest.fixture
def mock_actual_env_vars(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ACTUAL__URL", "https://actual.com")
    monkeypatch.setenv("ACTUAL__PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__ENCRYPTION_PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__FILE", "file")
