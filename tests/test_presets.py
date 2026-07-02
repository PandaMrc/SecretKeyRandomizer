from __future__ import annotations

from app.core.presets import PRESETS


def test_aes_256_preset_uses_exactly_32_bytes() -> None:
    assert PRESETS["aes_256"].byte_length == 32


def test_security_presets_use_at_least_32_bytes() -> None:
    for key in [
        "jwt",
        "api_key",
        "webhook",
        "hmac_sha256",
        "session",
        "csrf",
        "refresh_token",
        "database_encryption",
        "random_token",
    ]:
        assert PRESETS[key].byte_length >= 32


def test_salt_preset_uses_at_least_16_bytes() -> None:
    assert PRESETS["salt"].byte_length >= 16
