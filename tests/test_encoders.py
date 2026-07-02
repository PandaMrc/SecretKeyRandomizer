from __future__ import annotations

import re

from app.core.encoders import encode_base64url
from app.core.generator import generate_secret


def test_hex_output_contains_only_hex_characters() -> None:
    secret = generate_secret(32, "hex")

    assert re.fullmatch(r"[0-9a-f]+", secret)


def test_base64url_output_is_url_safe() -> None:
    secret = generate_secret(32, "base64url")

    assert "+" not in secret
    assert "/" not in secret
    assert "=" not in secret


def test_base64url_encoder_removes_padding() -> None:
    encoded = encode_base64url(b"abcde")

    assert "+" not in encoded
    assert "/" not in encoded
    assert "=" not in encoded
