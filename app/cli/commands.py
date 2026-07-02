"""Optional command-line interface."""

from __future__ import annotations

import argparse

from app.core.entropy import calculate_byte_entropy, calculate_charset_entropy, get_security_level
from app.core.formatters import format_env, format_json, format_plain
from app.core.generator import ASCII_SAFE_CHARSET, generate_secret
from app.core.presets import PRESETS, get_preset
from app.core.validators import normalize_charset, normalize_encoding, normalize_output_format


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="secretkeyrandomizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a secret")
    generate_parser.add_argument("--preset", default="jwt", help="Preset key, for example jwt or aes-256")
    generate_parser.add_argument("--bytes", dest="byte_length", type=int, help="Byte or character length")
    generate_parser.add_argument("--encoding", help="hex, base64, base64url, ascii-safe, custom-charset, uuid-v4")
    generate_parser.add_argument("--env", dest="env_name", help="ENV variable name")
    generate_parser.add_argument("--format", dest="output_format", default="plain", help="plain, env, or json")
    generate_parser.add_argument("--prefix", default=None)
    generate_parser.add_argument("--suffix", default=None)
    generate_parser.add_argument("--custom-charset", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        preset = get_preset(args.preset)
        encoding = normalize_encoding(args.encoding or preset.encoding)
        byte_length = args.byte_length or preset.byte_length
        prefix = preset.prefix if args.prefix is None else args.prefix
        suffix = preset.suffix if args.suffix is None else args.suffix
        env_name = args.env_name or preset.env_name
        output_format = normalize_output_format(args.output_format)
        custom_charset = args.custom_charset or ASCII_SAFE_CHARSET

        secret = generate_secret(
            byte_length=byte_length,
            encoding=encoding,
            prefix=prefix,
            suffix=suffix,
            custom_charset=custom_charset,
            output_length=byte_length,
        )

        entropy_bits = _estimate_entropy(encoding, byte_length, custom_charset)
        metadata = {
            "encoding": encoding,
            "bytes": None if encoding in {"ascii-safe", "custom-charset", "uuid-v4"} else byte_length,
            "length": byte_length if encoding in {"ascii-safe", "custom-charset"} else None,
            "estimated_entropy_bits": int(entropy_bits) if float(entropy_bits).is_integer() else round(entropy_bits, 2),
            "security_level": get_security_level(entropy_bits),
        }

        if output_format == "plain":
            print(format_plain(secret))
        elif output_format == "env":
            print(format_env(env_name, secret))
        elif output_format == "json":
            print(format_json(env_name, secret, metadata))
        else:
            parser.error("Unsupported output format.")
        return 0

    parser.error("Unsupported command.")
    return 2


def _estimate_entropy(encoding: str, byte_length: int, custom_charset: str) -> float:
    if encoding == "custom-charset":
        return calculate_charset_entropy(byte_length, len(normalize_charset(custom_charset)))
    if encoding == "ascii-safe":
        return calculate_charset_entropy(byte_length, len(ASCII_SAFE_CHARSET))
    if encoding == "uuid-v4":
        return 122.0
    return float(calculate_byte_entropy(byte_length))


if __name__ == "__main__":
    raise SystemExit(main())
