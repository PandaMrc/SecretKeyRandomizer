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
    category: str = "General"
    description: str = ""
    recommended_entropy_bits: int = 256
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
        category="Auth",
        description="General-purpose signing secret for JWT tokens.",
    ),
    "api_key": SecretPreset(
        key="api_key",
        name="API Key",
        env_name="API_KEY",
        byte_length=32,
        encoding="base64url",
        category="API",
        description="Public-facing API key value with a recognizable secret prefix.",
        prefix="sk_",
    ),
    "webhook": SecretPreset(
        key="webhook",
        name="Webhook Secret",
        env_name="WEBHOOK_SECRET",
        byte_length=32,
        encoding="base64url",
        category="API",
        description="Webhook signing secret for request verification.",
        prefix="whsec_",
    ),
    "aes_256": SecretPreset(
        key="aes_256",
        name="AES-256 Key",
        env_name="ENCRYPTION_KEY",
        byte_length=32,
        encoding="hex",
        category="Encryption",
        description="Raw 256-bit key material encoded as hex.",
        warning="AES requires a separate IV or nonce. Never reuse an IV or nonce with the same key.",
    ),
    "hmac_sha256": SecretPreset(
        key="hmac_sha256",
        name="HMAC-SHA256 Secret",
        env_name="HMAC_SECRET",
        byte_length=32,
        encoding="base64url",
        category="Auth",
        description="HMAC-SHA256 signing secret.",
    ),
    "session": SecretPreset(
        key="session",
        name="Session Secret",
        env_name="SESSION_SECRET",
        byte_length=32,
        encoding="base64url",
        category="Auth",
        description="Server-side session signing or encryption secret.",
    ),
    "csrf": SecretPreset(
        key="csrf",
        name="CSRF Secret",
        env_name="CSRF_SECRET",
        byte_length=32,
        encoding="base64url",
        category="Auth",
        description="CSRF token signing secret.",
    ),
    "refresh_token": SecretPreset(
        key="refresh_token",
        name="Refresh Token Secret",
        env_name="REFRESH_TOKEN_SECRET",
        byte_length=32,
        encoding="base64url",
        category="Auth",
        description="Refresh token signing or rotation secret.",
    ),
    "database_encryption": SecretPreset(
        key="database_encryption",
        name="Database Encryption Key",
        env_name="DATABASE_ENCRYPTION_KEY",
        byte_length=32,
        encoding="hex",
        category="Encryption",
        description="Database field or application-level encryption key.",
        warning="Store encryption keys securely. Never expose them in frontend or public environments.",
    ),
    "salt": SecretPreset(
        key="salt",
        name="Salt",
        env_name="SALT",
        byte_length=16,
        encoding="hex",
        category="General",
        description="Random salt value.",
        recommended_entropy_bits=128,
        warning="A salt does not need to be secret, but it should be sufficiently random.",
    ),
    "random_token": SecretPreset(
        key="random_token",
        name="Random Token",
        env_name="RANDOM_TOKEN",
        byte_length=32,
        encoding="base64url",
        category="General",
        description="General-purpose random token.",
    ),
    "django_secret_key": SecretPreset(
        key="django_secret_key",
        name="Django SECRET_KEY",
        env_name="DJANGO_SECRET_KEY",
        byte_length=50,
        encoding="ascii-safe",
        category="Framework",
        description="Django application SECRET_KEY.",
    ),
    "laravel_app_key": SecretPreset(
        key="laravel_app_key",
        name="Laravel APP_KEY",
        env_name="APP_KEY",
        byte_length=32,
        encoding="base64",
        category="Framework",
        description="Laravel application key value.",
        prefix="base64:",
    ),
    "rails_secret_key_base": SecretPreset(
        key="rails_secret_key_base",
        name="Rails SECRET_KEY_BASE",
        env_name="SECRET_KEY_BASE",
        byte_length=64,
        encoding="hex",
        category="Framework",
        description="Rails secret_key_base value.",
        recommended_entropy_bits=512,
    ),
    "nextauth_secret": SecretPreset(
        key="nextauth_secret",
        name="NextAuth Secret",
        env_name="NEXTAUTH_SECRET",
        byte_length=32,
        encoding="base64url",
        category="Framework",
        description="NextAuth.js secret.",
    ),
    "oauth_client_secret": SecretPreset(
        key="oauth_client_secret",
        name="OAuth Client Secret",
        env_name="OAUTH_CLIENT_SECRET",
        byte_length=32,
        encoding="base64url",
        category="API",
        description="OAuth client secret for confidential clients.",
    ),
}


TEMPLATE_PACKS: dict[str, tuple[str, tuple[str, ...]]] = {
    "web_api": (
        "Web API",
        ("api_key", "webhook", "random_token"),
    ),
    "auth_jwt": (
        "Auth / JWT",
        ("jwt", "session", "csrf", "refresh_token", "nextauth_secret"),
    ),
    "encryption": (
        "Encryption",
        ("aes_256", "database_encryption", "hmac_sha256", "salt"),
    ),
    "django": (
        "Django",
        ("django_secret_key", "database_encryption", "salt"),
    ),
    "laravel": (
        "Laravel",
        ("laravel_app_key", "session", "csrf"),
    ),
    "rails": (
        "Rails",
        ("rails_secret_key_base", "database_encryption", "salt"),
    ),
    "next_auth": (
        "Next / Auth",
        ("nextauth_secret", "jwt", "session", "csrf"),
    ),
}


def get_preset(key: str) -> SecretPreset:
    normalized = key.strip().lower().replace("-", "_")
    try:
        return PRESETS[normalized]
    except KeyError as exc:
        options = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset. Use one of: {options}.") from exc


def get_template_pack(key: str) -> tuple[str, tuple[SecretPreset, ...]]:
    normalized = key.strip().lower().replace("-", "_").replace(" ", "_")
    try:
        name, preset_keys = TEMPLATE_PACKS[normalized]
    except KeyError as exc:
        options = ", ".join(sorted(TEMPLATE_PACKS))
        raise ValueError(f"Unknown template pack. Use one of: {options}.") from exc
    return name, tuple(get_preset(preset_key) for preset_key in preset_keys)
