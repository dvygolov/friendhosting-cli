from __future__ import annotations

import json
from typing import Any


def success(command: str, data: dict[str, Any], **meta: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": True,
        "command": command,
        "data": data,
    }
    result.update({key: value for key, value in meta.items() if value is not None})
    return result


def error(command: str, message: str, *, error_code: str | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "command": command,
        "errorCode": error_code,
        "errorMsg": message,
    }
    if data is not None:
        result["data"] = data
    return result


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
