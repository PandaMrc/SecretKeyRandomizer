from __future__ import annotations

import pytest

from app.core.validators import normalize_charset, validate_byte_length, validate_encoding, validate_env_name


def test_validate_byte_length_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError):
        validate_byte_length(0)


def test_validate_encoding_accepts_supported_aliases() -> None:
    validate_encoding("custom charset")
    validate_encoding("uuid4")


def test_validate_env_name_accepts_standard_names() -> None:
    validate_env_name("DATABASE_ENCRYPTION_KEY")


def test_normalize_charset_removes_duplicates_in_order() -> None:
    assert normalize_charset("aabcc1") == "abc1"
