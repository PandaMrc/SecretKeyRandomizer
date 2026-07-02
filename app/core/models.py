"""Data models for generation workflows."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerationRequest:
    preset_key: str
    encoding: str
    byte_length: int
    env_name: str
    output_format: str = "env"
    prefix: str = ""
    suffix: str = ""
    custom_charset: str | None = None
    output_length: int | None = None


@dataclass(frozen=True)
class GeneratedSecret:
    preset_key: str
    name: str
    env_name: str
    value: str
    encoding: str
    byte_length: int | None
    length: int | None
    estimated_entropy_bits: int | float
    security_level: str
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def metadata(self) -> dict[str, object]:
        return {
            "preset": self.preset_key,
            "encoding": self.encoding,
            "bytes": self.byte_length,
            "length": self.length,
            "estimated_entropy_bits": self.estimated_entropy_bits,
            "security_level": self.security_level,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class GenerationBatch:
    name: str
    secrets: tuple[GeneratedSecret, ...]

    def first(self) -> GeneratedSecret | None:
        return self.secrets[0] if self.secrets else None
