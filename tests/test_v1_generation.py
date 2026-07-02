from __future__ import annotations

import json

from app.core.display import mask_secret
from app.core.formatters import format_env_block, format_json_array
from app.core.generator import generate_batch, generate_from_request, generate_template_pack, request_from_preset
from app.core.presets import PRESETS, TEMPLATE_PACKS


def test_generation_request_outputs_generated_secret_metadata() -> None:
    generated = generate_from_request(request_from_preset("jwt"))

    assert generated.preset_key == "jwt"
    assert generated.env_name == "JWT_SECRET"
    assert generated.security_level == "Very Strong"
    assert generated.estimated_entropy_bits == 256


def test_bulk_generation_count_env_names_and_uniqueness() -> None:
    requests = [request_from_preset("jwt"), request_from_preset("api_key"), request_from_preset("webhook")]
    batch = generate_batch("Bulk .env", requests)

    assert len(batch.secrets) == 3
    assert [secret.env_name for secret in batch.secrets] == ["JWT_SECRET", "API_KEY", "WEBHOOK_SECRET"]
    assert len({secret.value for secret in batch.secrets}) == 3


def test_template_pack_outputs_expected_framework_secret_names() -> None:
    batch = generate_template_pack("django")

    assert [secret.env_name for secret in batch.secrets] == [
        "DJANGO_SECRET_KEY",
        "DATABASE_ENCRYPTION_KEY",
        "SALT",
    ]


def test_all_template_pack_keys_resolve_to_existing_presets() -> None:
    for _template_key, (_template_name, preset_keys) in TEMPLATE_PACKS.items():
        for preset_key in preset_keys:
            assert preset_key in PRESETS


def test_bulk_formatters_emit_valid_env_and_json() -> None:
    batch = generate_template_pack("web_api")
    env_output = format_env_block(batch.secrets)
    json_output = format_json_array(batch)

    assert "API_KEY=" in env_output
    assert "WEBHOOK_SECRET=" in env_output
    payload = json.loads(json_output)
    assert payload["name"] == "Web API"
    assert len(payload["secrets"]) == 3


def test_mask_secret_keeps_secret_value_unchanged() -> None:
    secret = "abcdefghijklmnopqrstuvwxyz"
    masked = mask_secret(secret)

    assert secret == "abcdefghijklmnopqrstuvwxyz"
    assert masked.startswith("abcd")
    assert masked.endswith("wxyz")
    assert secret not in masked
