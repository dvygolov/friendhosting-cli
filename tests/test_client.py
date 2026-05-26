import httpx
import pytest

from friendhosting_cli.client import FriendhostingAPIError, FriendhostingClient
from friendhosting_cli.config import Credentials


def credentials() -> Credentials:
    return Credentials(login="user", api_key="key", api_url="https://example.test/api", source="env")


def test_request_posts_documented_fields() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode()
        return httpx.Response(200, json={"status": "SUCCESS", "balance": "10", "currency": "USD"})

    client = FriendhostingClient(credentials(), transport=httpx.MockTransport(handler))
    data = client.request("getBalance")

    assert data["status"] == "SUCCESS"
    body = captured["body"]
    assert "command=getBalance" in body
    assert "login=user" in body
    assert "apikey=key" in body
    assert "json=1" in body


def test_api_error_is_normalized() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"status": "ERROR", "errorCode": "5", "errorMsg": "Доступ к API отключен."},
        )

    client = FriendhostingClient(credentials(), transport=httpx.MockTransport(handler))

    with pytest.raises(FriendhostingAPIError) as exc:
        client.request("getBalance")

    assert exc.value.command == "getBalance"
    assert exc.value.error_code == "5"
    assert exc.value.error_msg == "Доступ к API отключен."
