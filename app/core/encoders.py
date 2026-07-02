"""Byte encoders used by the generator."""

from __future__ import annotations

import base64


def encode_hex(data: bytes) -> str:
    return data.hex()


def encode_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def encode_base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")
