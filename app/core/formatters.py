"""Output formatters."""

from __future__ import annotations

import json
from typing import Any

from .validators import validate_env_name


def format_plain(secret: str) -> str:
    return secret


def format_env(name: str, secret: str) -> str:
    normalized_name = name.strip()
    validate_env_name(normalized_name)
    return f"{normalized_name}={secret}"


def format_json(name: str, secret: str, metadata: dict[str, Any]) -> str:
    normalized_name = name.strip()
    validate_env_name(normalized_name)
    payload = {
        "name": normalized_name,
        "value": secret,
        **metadata,
    }
    return json.dumps(payload, indent=2, sort_keys=False)
