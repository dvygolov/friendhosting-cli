from __future__ import annotations

from typing import Any

import httpx

from .config import Credentials


class FriendhostingAPIError(RuntimeError):
    def __init__(self, command: str, error_code: str | None, error_msg: str | None, data: dict[str, Any]):
        self.command = command
        self.error_code = error_code
        self.error_msg = error_msg
        self.data = data
        super().__init__(error_msg or "Friendhosting API error")


class FriendhostingClient:
    def __init__(self, credentials: Credentials, timeout: float = 30.0, transport: httpx.BaseTransport | None = None) -> None:
        self.credentials = credentials
        self.timeout = timeout
        self.transport = transport

    def request(self, command: str, **params: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "command": command,
            "login": self.credentials.login,
            "apikey": self.credentials.api_key,
            "json": "1",
        }
        payload.update({key: value for key, value in params.items() if value is not None and value != ""})

        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            response = client.post(self.credentials.api_url, data=payload)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, dict):
            raise FriendhostingAPIError(command, None, "Friendhosting returned a non-object JSON response.", {"raw": data})

        if data.get("status") == "ERROR":
            raise FriendhostingAPIError(
                command=command,
                error_code=str(data.get("errorCode")) if data.get("errorCode") is not None else None,
                error_msg=str(data.get("errorMsg")) if data.get("errorMsg") is not None else None,
                data=data,
            )

        return data
