"""Entropy estimation and security level helpers."""

from __future__ import annotations

import math

from .validators import validate_byte_length, validate_text_length


def calculate_byte_entropy(byte_length: int) -> int:
    validate_byte_length(byte_length)
    return byte_length * 8


def calculate_charset_entropy(length: int, charset_size: int) -> float:
    validate_text_length(length)
    if not isinstance(charset_size, int):
        raise ValueError("Charset size must be an integer.")
    if charset_size < 2:
        raise ValueError("Charset size must be at least two.")
    return length * math.log2(charset_size)


def get_security_level(entropy_bits: float) -> str:
    if entropy_bits < 0:
        raise ValueError("Entropy cannot be negative.")
    if entropy_bits < 64:
        return "Weak"
    if entropy_bits < 128:
        return "Medium"
    if entropy_bits < 256:
        return "Strong"
    return "Very Strong"


def get_entropy_warning(entropy_bits: float) -> str | None:
    if entropy_bits < 64:
        return "Entropy is weak. Increase length before using this as a secret."
    if entropy_bits < 128:
        return "Entropy is medium. Use at least 128 bits for most secrets."
    if entropy_bits < 256:
        return "Entropy is below the 256-bit default recommendation for security presets."
    return None
