"""Cryptographically secure secret generation."""

from __future__ import annotations

import secrets
import uuid

from .encoders import encode_base64, encode_base64url, encode_hex
from .entropy import calculate_byte_entropy, calculate_charset_entropy, get_entropy_warning, get_security_level
from .models import GeneratedSecret, GenerationBatch, GenerationRequest
from .presets import SecretPreset, get_preset, get_template_pack
from .validators import (
    normalize_charset,
    normalize_encoding,
    normalize_output_format,
    validate_byte_length,
    validate_charset,
    validate_encoding,
    validate_env_name,
    validate_output_format,
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


def request_from_preset(
    preset_key: str,
    output_format: str = "env",
    encoding: str | None = None,
    byte_length: int | None = None,
    env_name: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    custom_charset: str | None = None,
) -> GenerationRequest:
    preset = get_preset(preset_key)
    return GenerationRequest(
        preset_key=preset.key,
        encoding=encoding or preset.encoding,
        byte_length=byte_length or preset.byte_length,
        env_name=env_name or preset.env_name,
        output_format=output_format,
        prefix=preset.prefix if prefix is None else prefix,
        suffix=preset.suffix if suffix is None else suffix,
        custom_charset=custom_charset,
        output_length=byte_length or preset.byte_length,
    )


def generate_from_request(request: GenerationRequest) -> GeneratedSecret:
    encoding = normalize_encoding(request.encoding)
    output_format = normalize_output_format(request.output_format)
    validate_encoding(encoding)
    validate_output_format(output_format)
    validate_byte_length(request.byte_length)
    validate_env_name(request.env_name)

    preset = get_preset(request.preset_key)
    custom_charset = request.custom_charset or ASCII_SAFE_CHARSET
    value = generate_secret(
        byte_length=request.byte_length,
        encoding=encoding,
        prefix=request.prefix,
        suffix=request.suffix,
        custom_charset=custom_charset,
        output_length=request.output_length or request.byte_length,
    )
    entropy_bits = _estimate_entropy(encoding, request.byte_length, custom_charset)
    security_level = get_security_level(entropy_bits)
    warnings = _warnings_for(preset, encoding, entropy_bits)
    return GeneratedSecret(
        preset_key=preset.key,
        name=preset.name,
        env_name=request.env_name,
        value=value,
        encoding=encoding,
        byte_length=None if encoding in {"ascii-safe", "custom-charset", "uuid-v4"} else request.byte_length,
        length=request.byte_length if encoding in {"ascii-safe", "custom-charset"} else None,
        estimated_entropy_bits=_display_entropy_number(entropy_bits),
        security_level=security_level,
        warnings=warnings,
    )


def generate_batch(name: str, requests: list[GenerationRequest] | tuple[GenerationRequest, ...]) -> GenerationBatch:
    return GenerationBatch(name=name, secrets=tuple(generate_from_request(request) for request in requests))


def generate_template_pack(template_key: str, output_format: str = "env") -> GenerationBatch:
    name, presets = get_template_pack(template_key)
    requests = [request_from_preset(preset.key, output_format=output_format) for preset in presets]
    return generate_batch(name, requests)


def _estimate_entropy(encoding: str, byte_length: int, custom_charset: str) -> float:
    if encoding == "custom-charset":
        return calculate_charset_entropy(byte_length, len(normalize_charset(custom_charset)))
    if encoding == "ascii-safe":
        return calculate_charset_entropy(byte_length, len(ASCII_SAFE_CHARSET))
    if encoding == "uuid-v4":
        return 122.0
    return float(calculate_byte_entropy(byte_length))


def _warnings_for(preset: SecretPreset, encoding: str, entropy_bits: float) -> tuple[str, ...]:
    warnings: list[str] = []
    if preset.warning:
        warnings.append(preset.warning)
    if encoding == "uuid-v4":
        warnings.append("UUID values are useful as public identifiers, not high-security secret keys.")
    entropy_warning = get_entropy_warning(entropy_bits)
    if entropy_warning:
        warnings.append(entropy_warning)
    return tuple(warnings)


def _display_entropy_number(entropy_bits: float) -> int | float:
    if float(entropy_bits).is_integer():
        return int(entropy_bits)
    return round(entropy_bits, 2)
