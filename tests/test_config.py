import json
from pathlib import Path

import pytest

from friendhosting_cli.config import MissingCredentialsError, credential_status, load_credentials, write_config


def test_env_credentials_take_precedence(monkeypatch, tmp_path: Path) -> None:
    write_config("config-login", "config-key", cwd=tmp_path)
    monkeypatch.setenv("FRIENDHOSTING_LOGIN", "env-login")
    monkeypatch.setenv("FRIENDHOSTING_API_KEY", "env-key")

    creds = load_credentials(tmp_path)

    assert creds.source == "env"
    assert creds.login == "env-login"
    assert creds.api_key == "env-key"


def test_project_config_credentials(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FRIENDHOSTING_LOGIN", raising=False)
    monkeypatch.delenv("FRIENDHOSTING_API_KEY", raising=False)
    write_config("config-login", "config-key", cwd=tmp_path)

    creds = load_credentials(tmp_path)

    assert creds.source == "config"
    assert creds.login == "config-login"
    assert creds.api_key == "config-key"


def test_missing_credentials(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FRIENDHOSTING_LOGIN", raising=False)
    monkeypatch.delenv("FRIENDHOSTING_API_KEY", raising=False)

    with pytest.raises(MissingCredentialsError):
        load_credentials(tmp_path)


def test_auth_status_does_not_expose_key(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FRIENDHOSTING_LOGIN", "env-login")
    monkeypatch.setenv("FRIENDHOSTING_API_KEY", "secret-key")

    status = credential_status(tmp_path)

    assert status["active_source"] == "env"
    assert "secret-key" not in json.dumps(status)
