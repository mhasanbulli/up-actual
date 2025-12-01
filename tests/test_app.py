import datetime
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner
from up.app import app
from up.config import Settings

runner = CliRunner()


def test_get_settings(mock_actual_env_vars: pytest.MonkeyPatch):  # noqa: ARG001
    settings = Settings()  # type: ignore

    assert settings.url.get_secret_value() == "https://actual.com"
    assert settings.password.get_secret_value() == "password"
    assert settings.encryption_password.get_secret_value() == "password"
    assert settings.file == "file"


@patch("up.app.reconcile_accounts")
@patch("up.app.get_account_transaction_urls")
@patch("up.app.ActualSession")
@patch("up.app.Settings")
@patch("up.app.UpAPI")
def test_reconcile_command_default_parameters(
    mock_up_api: MagicMock,  # noqa: ARG001
    mock_settings: MagicMock,
    mock_actual_session: MagicMock,
    mock_get_accounts: MagicMock,
    mock_reconcile: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("UP_TOKEN", "test_token")
    monkeypatch.setenv("ACTUAL__URL", "https://actual.com")
    monkeypatch.setenv("ACTUAL__PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__ENCRYPTION_PASSWORD", "enc_password")
    monkeypatch.setenv("ACTUAL__FILE", "test_file")

    mock_settings.return_value.url.get_secret_value.return_value = "https://actual.com"
    mock_settings.return_value.password.get_secret_value.return_value = "password"
    mock_settings.return_value.encryption_password.get_secret_value.return_value = "enc_password"
    mock_settings.return_value.file = "test_file"

    mock_actual_instance = MagicMock()
    mock_actual_session.return_value.get_actual_session.return_value = mock_actual_instance

    mock_get_accounts.return_value = []

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    mock_reconcile.assert_called_once()

    call_args = mock_reconcile.call_args
    query_params = call_args[0][3]
    assert query_params.page_size == 100
    assert query_params.days_offset == 0


@patch("up.app.reconcile_accounts")
@patch("up.app.get_account_transaction_urls")
@patch("up.app.ActualSession")
@patch("up.app.Settings")
@patch("up.app.UpAPI")
def test_reconcile_command_with_start_date(
    mock_up_api: MagicMock,  # noqa: ARG001
    mock_settings: MagicMock,
    mock_actual_session: MagicMock,
    mock_get_accounts: MagicMock,
    mock_reconcile: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("UP_TOKEN", "test_token")
    monkeypatch.setenv("ACTUAL__URL", "https://actual.com")
    monkeypatch.setenv("ACTUAL__PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__ENCRYPTION_PASSWORD", "enc_password")
    monkeypatch.setenv("ACTUAL__FILE", "test_file")

    mock_settings.return_value.url.get_secret_value.return_value = "https://actual.com"
    mock_settings.return_value.password.get_secret_value.return_value = "password"
    mock_settings.return_value.encryption_password.get_secret_value.return_value = "enc_password"
    mock_settings.return_value.file = "test_file"

    mock_actual_instance = MagicMock()
    mock_actual_session.return_value.get_actual_session.return_value = mock_actual_instance

    mock_get_accounts.return_value = []

    result = runner.invoke(app, ["--start-date", "2025-01-01"])

    assert result.exit_code == 0
    mock_reconcile.assert_called_once()

    call_args = mock_reconcile.call_args
    query_params = call_args[0][3]
    assert query_params.start_date == datetime.datetime(2025, 1, 1)


@patch("up.app.reconcile_accounts")
@patch("up.app.get_account_transaction_urls")
@patch("up.app.ActualSession")
@patch("up.app.Settings")
@patch("up.app.UpAPI")
def test_reconcile_command_with_days_back(
    mock_up_api: MagicMock,  # noqa: ARG001
    mock_settings: MagicMock,
    mock_actual_session: MagicMock,
    mock_get_accounts: MagicMock,
    mock_reconcile: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("UP_TOKEN", "test_token")
    monkeypatch.setenv("ACTUAL__URL", "https://actual.com")
    monkeypatch.setenv("ACTUAL__PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__ENCRYPTION_PASSWORD", "enc_password")
    monkeypatch.setenv("ACTUAL__FILE", "test_file")

    mock_settings.return_value.url.get_secret_value.return_value = "https://actual.com"
    mock_settings.return_value.password.get_secret_value.return_value = "password"
    mock_settings.return_value.encryption_password.get_secret_value.return_value = "enc_password"
    mock_settings.return_value.file = "test_file"

    mock_actual_instance = MagicMock()
    mock_actual_session.return_value.get_actual_session.return_value = mock_actual_instance

    mock_get_accounts.return_value = []

    result = runner.invoke(app, ["--days-back", "90"])

    assert result.exit_code == 0
    mock_reconcile.assert_called_once()


@patch("up.app.reconcile_accounts")
@patch("up.app.get_account_transaction_urls")
@patch("up.app.ActualSession")
@patch("up.app.Settings")
@patch("up.app.UpAPI")
def test_reconcile_command_with_page_size(
    mock_up_api: MagicMock,  # noqa: ARG001
    mock_settings: MagicMock,
    mock_actual_session: MagicMock,
    mock_get_accounts: MagicMock,
    mock_reconcile: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("UP_TOKEN", "test_token")
    monkeypatch.setenv("ACTUAL__URL", "https://actual.com")
    monkeypatch.setenv("ACTUAL__PASSWORD", "password")
    monkeypatch.setenv("ACTUAL__ENCRYPTION_PASSWORD", "enc_password")
    monkeypatch.setenv("ACTUAL__FILE", "test_file")

    mock_settings.return_value.url.get_secret_value.return_value = "https://actual.com"
    mock_settings.return_value.password.get_secret_value.return_value = "password"
    mock_settings.return_value.encryption_password.get_secret_value.return_value = "enc_password"
    mock_settings.return_value.file = "test_file"

    mock_actual_instance = MagicMock()
    mock_actual_session.return_value.get_actual_session.return_value = mock_actual_instance

    mock_get_accounts.return_value = []

    result = runner.invoke(app, ["--page-size", "50"])

    assert result.exit_code == 0
    mock_reconcile.assert_called_once()

    call_args = mock_reconcile.call_args
    query_params = call_args[0][3]
    assert query_params.page_size == 50


def test_reconcile_command_invalid_date_format():
    result = runner.invoke(app, ["--start-date", "invalid-date"])

    assert result.exit_code == 1
    assert "Invalid date format" in result.output


def test_reconcile_command_help():
    result = runner.invoke(app, ["reconcile", "--help"])

    # Debug: Print the actual output
    print("\n=== DEBUG: Full help output ===")
    print(f"Exit code: {result.exit_code}")
    print(f"Output length: {len(result.output)}")
    print(f"Output:\n{result.output}")
    print("=== END DEBUG ===\n")

    assert result.exit_code == 0
    assert "Reconcile transactions from Up Banking to Actual Budget" in result.output
    assert "--start-date" in result.output
    assert "--days-back" in result.output
    assert "--page-size" in result.output
