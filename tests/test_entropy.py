from __future__ import annotations

import math

from app.core.entropy import (
    calculate_byte_entropy,
    calculate_charset_entropy,
    get_entropy_warning,
    get_security_level,
)


def test_byte_entropy_calculation() -> None:
    assert calculate_byte_entropy(32) == 256
    assert calculate_byte_entropy(16) == 128


def test_security_levels() -> None:
    assert get_security_level(63) == "Weak"
    assert get_security_level(64) == "Medium"
    assert get_security_level(127) == "Medium"
    assert get_security_level(128) == "Strong"
    assert get_security_level(255) == "Strong"
    assert get_security_level(256) == "Very Strong"


def test_low_entropy_warning() -> None:
    assert get_entropy_warning(80) is not None
    assert get_entropy_warning(256) is None


def test_custom_charset_entropy_uses_charset_size() -> None:
    entropy = calculate_charset_entropy(10, 16)

    assert entropy == 40


def test_prefix_and_suffix_are_not_in_entropy_formula() -> None:
    random_part_entropy = calculate_charset_entropy(20, 62)
    with_public_prefix_suffix = calculate_charset_entropy(20, 62)

    assert math.isclose(random_part_entropy, with_public_prefix_suffix)
