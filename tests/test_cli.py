import json

import pytest
from typer.testing import CliRunner

from friendhosting_cli.cli import app
from friendhosting_cli.client import FriendhostingAPIError


runner = CliRunner()


def parse_json(output: str) -> dict:
    return json.loads(output)


def test_mutating_command_requires_yes() -> None:
    result = runner.invoke(app, ["restart", "--order-id", "123"])

    assert result.exit_code == 2
    data = parse_json(result.output)
    assert data["ok"] is False
    assert data["errorCode"] == "CONFIRMATION_REQUIRED"


def test_missing_credentials_returns_json(monkeypatch) -> None:
    monkeypatch.delenv("FRIENDHOSTING_LOGIN", raising=False)
    monkeypatch.delenv("FRIENDHOSTING_API_KEY", raising=False)
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["balance"])

    assert result.exit_code == 2
    data = parse_json(result.output)
    assert data["ok"] is False
    assert data["errorCode"] == "MISSING_CREDENTIALS"
    assert "friendhosting auth setup" in data["errorMsg"]


def test_auth_setup_writes_project_config() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["auth", "setup", "--login", "demo-login", "--api-key", "demo-key"])

        assert result.exit_code == 0
        data = parse_json(result.output)
        assert data["ok"] is True
        assert data["data"]["login"] == "demo-login"
        assert "demo-key" not in result.output


@pytest.mark.parametrize(
    ("args", "expected_command", "expected_params"),
    [
        (["balance"], "getBalance", {}),
        (["tariffs", "--type", "vds"], "getTarifs", {"vid": "vds"}),
        (["orders"], "getOrders", {"orderid": None}),
        (["orders", "--order-id", "123"], "getOrders", {"orderid": "123"}),
        (
            ["create", "--type", "vds", "--tariff-id", "10", "--period", "1", "--domain", "example.com", "--addons", "4,5", "--yes"],
            "createOrder",
            {"vid": "vds", "tarifid": "10", "period": "1", "domain": "example.com", "addons": "4,5"},
        ),
        (["renew", "--order-id", "123", "--period", "1", "--yes"], "renewOrder", {"orderid": "123", "period": "1"}),
        (["suspend", "--order-id", "123", "--yes"], "suspendOrder", {"orderid": "123"}),
        (["unsuspend", "--order-id", "123", "--yes"], "unSuspendOrder", {"orderid": "123"}),
        (["restart", "--order-id", "123", "--yes"], "restartOrder", {"orderid": "123"}),
        (["reinstall", "--order-id", "123", "--yes"], "reinstallOrder", {"orderid": "123"}),
    ],
)
def test_cli_command_mappings(monkeypatch, args, expected_command, expected_params) -> None:
    calls = []

    class FakeClient:
        def request(self, command, **params):
            calls.append((command, params))
            return {"status": "SUCCESS", "echo": params}

    monkeypatch.setattr("friendhosting_cli.cli._client", lambda: FakeClient())

    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert calls == [(expected_command, expected_params)]
    data = parse_json(result.output)
    assert data["ok"] is True
    assert data["command"] == expected_command


def test_cli_api_error_json(monkeypatch) -> None:
    class FakeClient:
        def request(self, command, **params):
            raise FriendhostingAPIError(command, "5", "Доступ к API отключен.", {"status": "ERROR", "errorCode": "5"})

    monkeypatch.setattr("friendhosting_cli.cli._client", lambda: FakeClient())

    result = runner.invoke(app, ["balance"])

    assert result.exit_code == 1
    data = parse_json(result.output)
    assert data["ok"] is False
    assert data["errorCode"] == "5"
    assert data["errorMsg"] == "Доступ к API отключен."
