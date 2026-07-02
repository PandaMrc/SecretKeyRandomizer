from __future__ import annotations

import inspect

from app.core import generator
from app.core.generator import generate_custom_charset_secret, generate_secret


def test_same_settings_generate_different_values() -> None:
    first = generate_secret(32, "base64url")
    second = generate_secret(32, "base64url")

    assert first != second


def test_1000_generations_have_no_duplicates() -> None:
    values = {generate_secret(32, "base64url") for _ in range(1000)}

    assert len(values) == 1000


def test_prefix_and_suffix_are_applied() -> None:
    secret = generate_secret(32, "base64url", prefix="sk_", suffix="_end")

    assert secret.startswith("sk_")
    assert secret.endswith("_end")


def test_custom_charset_uses_only_normalized_charset_characters() -> None:
    secret = generate_custom_charset_secret(128, "aabbcc0011")

    assert set(secret) <= set("abc01")


def test_generator_does_not_import_or_call_random_module() -> None:
    source = inspect.getsource(generator)

    assert "import random" not in source
    assert "from random" not in source
    assert "random." not in source


def test_secret_values_are_not_logged(caplog) -> None:
    secret = generate_secret(32, "base64url")

    assert secret not in caplog.text
