"""Built-in secret presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecretPreset:
    key: str
    name: str
    env_name: str
    byte_length: int
    encoding: str
    prefix: str = ""
    suffix: str = ""
    warning: str | None = None


PRESETS = {
    "jwt": SecretPreset(
        key="jwt",
        name="JWT Secret",
        env_name="JWT_SECRET",
        byte_length=32,
        encoding="base64url",
    ),
    "api_key": SecretPreset(
        key="api_key",
        name="API Key",
        env_name="API_KEY",
        byte_length=32,
        encoding="base64url",
        prefix="sk_",
    ),
    "webhook": SecretPreset(
        key="webhook",
        name="Webhook Secret",
        env_name="WEBHOOK_SECRET",
        byte_length=32,
        encoding="base64url",
        prefix="whsec_",
    ),
    "aes_256": SecretPreset(
        key="aes_256",
        name="AES-256 Key",
        env_name="ENCRYPTION_KEY",
        byte_length=32,
        encoding="hex",
        warning="AES requires a separate IV or nonce. Never reuse an IV or nonce with the same key.",
    ),
    "hmac_sha256": SecretPreset(
        key="hmac_sha256",
        name="HMAC-SHA256 Secret",
        env_name="HMAC_SECRET",
        byte_length=32,
        encoding="base64url",
    ),
    "session": SecretPreset(
        key="session",
        name="Session Secret",
        env_name="SESSION_SECRET",
        byte_length=32,
        encoding="base64url",
    ),
    "csrf": SecretPreset(
        key="csrf",
        name="CSRF Secret",
        env_name="CSRF_SECRET",
        byte_length=32,
        encoding="base64url",
    ),
    "refresh_token": SecretPreset(
        key="refresh_token",
        name="Refresh Token Secret",
        env_name="REFRESH_TOKEN_SECRET",
        byte_length=32,
        encoding="base64url",
    ),
    "database_encryption": SecretPreset(
        key="database_encryption",
        name="Database Encryption Key",
        env_name="DATABASE_ENCRYPTION_KEY",
        byte_length=32,
        encoding="hex",
        warning="Store encryption keys securely. Never expose them in frontend or public environments.",
    ),
    "salt": SecretPreset(
        key="salt",
        name="Salt",
        env_name="SALT",
        byte_length=16,
        encoding="hex",
        warning="A salt does not need to be secret, but it should be sufficiently random.",
    ),
    "random_token": SecretPreset(
        key="random_token",
        name="Random Token",
        env_name="RANDOM_TOKEN",
        byte_length=32,
        encoding="base64url",
    ),
}


def get_preset(key: str) -> SecretPreset:
    normalized = key.strip().lower().replace("-", "_")
    try:
        return PRESETS[normalized]
    except KeyError as exc:
        options = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset. Use one of: {options}.") from exc
