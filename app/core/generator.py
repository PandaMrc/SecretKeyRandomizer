"""Cryptographically secure secret generation."""

from __future__ import annotations

import secrets
import uuid

from .encoders import encode_base64, encode_base64url, encode_hex
from .validators import (
    normalize_charset,
    normalize_encoding,
    validate_byte_length,
    validate_charset,
    validate_encoding,
    validate_text_length,
)


ASCII_SAFE_CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_random_bytes(byte_length: int) -> bytes:
    validate_byte_length(byte_length)
    return secrets.token_bytes(byte_length)


def generate_custom_charset_secret(length: int, charset: str) -> str:
    validate_text_length(length)
    validate_charset(charset)
    normalized_charset = normalize_charset(charset)
    return "".join(secrets.choice(normalized_charset) for _ in range(length))


def generate_secret(
    byte_length: int,
    encoding: str,
    prefix: str = "",
    suffix: str = "",
    custom_charset: str | None = None,
    output_length: int | None = None,
) -> str:
    validate_byte_length(byte_length)
    validate_encoding(encoding)
    normalized_encoding = normalize_encoding(encoding)

    if normalized_encoding == "custom-charset":
        if custom_charset is None:
            raise ValueError("Custom charset is required for custom-charset encoding.")
        random_part = generate_custom_charset_secret(output_length or byte_length, custom_charset)
    elif normalized_encoding == "ascii-safe":
        random_part = generate_custom_charset_secret(output_length or byte_length, ASCII_SAFE_CHARSET)
    elif normalized_encoding == "uuid-v4":
        random_part = str(uuid.uuid4())
    else:
        random_bytes = generate_random_bytes(byte_length)
        if normalized_encoding == "hex":
            random_part = encode_hex(random_bytes)
        elif normalized_encoding == "base64":
            random_part = encode_base64(random_bytes)
        elif normalized_encoding == "base64url":
            random_part = encode_base64url(random_bytes)
        else:
            raise ValueError("Unsupported encoding.")

    return f"{prefix}{random_part}{suffix}"
