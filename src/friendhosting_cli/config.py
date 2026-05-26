from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


DEFAULT_API_URL = "https://my.friendhosting.net/apih.php"
CONFIG_DIR = ".friendhosting"
CONFIG_FILE = "config.json"


class Credentials(BaseModel):
    login: str
    api_key: str = Field(repr=False)
    api_url: str = DEFAULT_API_URL
    source: Literal["env", "config"]

    @property
    def masked_api_key(self) -> str:
        if len(self.api_key) <= 4:
            return "****"
        return f"{self.api_key[:2]}...{self.api_key[-2:]}"


class MissingCredentialsError(RuntimeError):
    pass


def config_path(cwd: Path | None = None) -> Path:
    root = cwd or Path.cwd()
    return root / CONFIG_DIR / CONFIG_FILE


def load_config(path: Path | None = None) -> dict[str, str] | None:
    cfg_path = path or config_path()
    if not cfg_path.exists():
        return None

    with cfg_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Config must be a JSON object: {cfg_path}")

    return {str(key): str(value) for key, value in data.items() if value is not None}


def write_config(login: str, api_key: str, api_url: str = DEFAULT_API_URL, cwd: Path | None = None) -> Path:
    cfg_path = config_path(cwd)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "login": login,
        "api_key": api_key,
        "api_url": api_url,
    }
    with cfg_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return cfg_path


def load_credentials(cwd: Path | None = None) -> Credentials:
    env_login = os.getenv("FRIENDHOSTING_LOGIN")
    env_api_key = os.getenv("FRIENDHOSTING_API_KEY")
    env_api_url = os.getenv("FRIENDHOSTING_API_URL") or DEFAULT_API_URL

    if env_login and env_api_key:
        return Credentials(login=env_login, api_key=env_api_key, api_url=env_api_url, source="env")

    cfg = load_config(config_path(cwd))
    if cfg:
        login = cfg.get("login")
        api_key = cfg.get("api_key") or cfg.get("apikey") or cfg.get("apiKey")
        api_url = os.getenv("FRIENDHOSTING_API_URL") or cfg.get("api_url") or DEFAULT_API_URL
        if login and api_key:
            return Credentials(login=login, api_key=api_key, api_url=api_url, source="config")

    raise MissingCredentialsError(
        "Friendhosting credentials are missing. Set FRIENDHOSTING_LOGIN and "
        "FRIENDHOSTING_API_KEY, or run `friendhosting auth setup` in this project."
    )


def credential_status(cwd: Path | None = None) -> dict[str, object]:
    cfg_path = config_path(cwd)
    env_ready = bool(os.getenv("FRIENDHOSTING_LOGIN") and os.getenv("FRIENDHOSTING_API_KEY"))
    cfg = load_config(cfg_path)
    config_ready = bool(cfg and cfg.get("login") and (cfg.get("api_key") or cfg.get("apikey") or cfg.get("apiKey")))

    active_source = None
    login = None
    api_url = os.getenv("FRIENDHOSTING_API_URL") or DEFAULT_API_URL
    if env_ready:
        active_source = "env"
        login = os.getenv("FRIENDHOSTING_LOGIN")
    elif config_ready and cfg:
        active_source = "config"
        login = cfg.get("login")
        api_url = os.getenv("FRIENDHOSTING_API_URL") or cfg.get("api_url") or DEFAULT_API_URL

    return {
        "env_ready": env_ready,
        "config_ready": config_ready,
        "active_source": active_source,
        "login": login,
        "api_url": api_url,
        "config_path": str(cfg_path),
    }
