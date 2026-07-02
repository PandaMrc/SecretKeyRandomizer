"""Output formatters."""

from __future__ import annotations

import json
from typing import Any

from .models import GeneratedSecret, GenerationBatch
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


def format_generated_json(generated: GeneratedSecret) -> str:
    return json.dumps(_generated_payload(generated), indent=2, sort_keys=False)


def format_env_block(secrets: tuple[GeneratedSecret, ...] | list[GeneratedSecret]) -> str:
    lines = []
    for generated in secrets:
        validate_env_name(generated.env_name)
        lines.append(f"{generated.env_name}={generated.value}")
    return "\n".join(lines)


def format_json_array(batch: GenerationBatch) -> str:
    payload = {
        "name": batch.name,
        "secrets": [_generated_payload(generated) for generated in batch.secrets],
    }
    return json.dumps(payload, indent=2, sort_keys=False)


def _generated_payload(generated: GeneratedSecret) -> dict[str, Any]:
    return {
        "name": generated.env_name,
        "value": generated.value,
        **generated.metadata(),
    }
