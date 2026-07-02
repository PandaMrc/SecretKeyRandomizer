from __future__ import annotations

import json

import pytest

from app.core.formatters import format_env, format_json


def test_env_formatter_outputs_env_assignment() -> None:
    assert format_env("JWT_SECRET", "<generate-with-secretkeyrandomizer>") == (
        "JWT_SECRET=<generate-with-secretkeyrandomizer>"
    )


def test_env_formatter_rejects_invalid_name() -> None:
    with pytest.raises(ValueError):
        format_env("1_INVALID", "<generate-with-secretkeyrandomizer>")


def test_json_formatter_outputs_valid_json() -> None:
    formatted = format_json(
        "JWT_SECRET",
        "<generate-with-secretkeyrandomizer>",
        {
            "encoding": "base64url",
            "bytes": 32,
            "estimated_entropy_bits": 256,
            "security_level": "Very Strong",
        },
    )

    payload = json.loads(formatted)
    assert payload["name"] == "JWT_SECRET"
    assert payload["value"] == "<generate-with-secretkeyrandomizer>"
    assert payload["estimated_entropy_bits"] == 256
