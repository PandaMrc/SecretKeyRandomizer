"""Validation helpers for SecretKeyRandomizer."""

from __future__ import annotations

import re


ALLOWED_ENCODINGS = {
    "hex",
    "base64",
    "base64url",
    "ascii-safe",
    "custom-charset",
    "uuid-v4",
}

ALLOWED_OUTPUT_FORMATS = {"plain", "env", "json"}
MAX_BYTE_LENGTH = 4096
MAX_TEXT_LENGTH = 8192
ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def normalize_encoding(encoding: str) -> str:
    normalized = encoding.strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "ascii": "ascii-safe",
        "asciisafe": "ascii-safe",
        "custom": "custom-charset",
        "customcharset": "custom-charset",
        "custom-charset-output": "custom-charset",
        "uuid": "uuid-v4",
        "uuid4": "uuid-v4",
    }
    return aliases.get(normalized, normalized)


def normalize_output_format(output_format: str) -> str:
    normalized = output_format.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized == "text":
        return "plain"
    if normalized == "dotenv":
        return "env"
    return normalized


def normalize_charset(charset: str) -> str:
    seen: set[str] = set()
    normalized_chars: list[str] = []
    for char in charset:
        if char not in seen:
            seen.add(char)
            normalized_chars.append(char)
    return "".join(normalized_chars)


def validate_byte_length(byte_length: int) -> None:
    if not isinstance(byte_length, int):
        raise ValueError("Byte length must be an integer.")
    if byte_length <= 0:
        raise ValueError("Byte length must be greater than zero.")
    if byte_length > MAX_BYTE_LENGTH:
        raise ValueError(f"Byte length must be {MAX_BYTE_LENGTH} or less.")


def validate_text_length(length: int) -> None:
    if not isinstance(length, int):
        raise ValueError("Length must be an integer.")
    if length <= 0:
        raise ValueError("Length must be greater than zero.")
    if length > MAX_TEXT_LENGTH:
        raise ValueError(f"Length must be {MAX_TEXT_LENGTH} or less.")


def validate_charset(charset: str) -> None:
    if not isinstance(charset, str):
        raise ValueError("Custom charset must be text.")
    normalized = normalize_charset(charset)
    if not normalized:
        raise ValueError("Custom charset cannot be empty.")
    if len(normalized) < 2:
        raise ValueError("Custom charset must contain at least two unique characters.")


def validate_encoding(encoding: str) -> None:
    if normalize_encoding(encoding) not in ALLOWED_ENCODINGS:
        options = ", ".join(sorted(ALLOWED_ENCODINGS))
        raise ValueError(f"Unsupported encoding. Use one of: {options}.")


def validate_env_name(name: str) -> None:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("ENV name cannot be empty.")
    if not ENV_NAME_PATTERN.fullmatch(name.strip()):
        raise ValueError("ENV name must match [A-Za-z_][A-Za-z0-9_]*.")


def validate_output_format(output_format: str) -> None:
    if normalize_output_format(output_format) not in ALLOWED_OUTPUT_FORMATS:
        options = ", ".join(sorted(ALLOWED_OUTPUT_FORMATS))
        raise ValueError(f"Unsupported output format. Use one of: {options}.")
