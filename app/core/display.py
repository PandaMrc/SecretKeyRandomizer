"""Display helpers that never alter the underlying secret value."""

from __future__ import annotations


def mask_secret(value: str, visible_prefix: int = 4, visible_suffix: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= visible_prefix + visible_suffix:
        return "•" * len(value)
    return f"{value[:visible_prefix]}{'•' * 12}{value[-visible_suffix:]}"
