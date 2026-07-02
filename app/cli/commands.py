"""Optional command-line interface."""

from __future__ import annotations

import argparse

from app.core.formatters import format_env, format_env_block, format_generated_json, format_json_array, format_plain
from app.core.generator import generate_batch, generate_from_request, generate_template_pack, request_from_preset
from app.core.models import GeneratedSecret, GenerationBatch
from app.core.presets import PRESETS, TEMPLATE_PACKS, get_preset
from app.core.validators import normalize_output_format


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="secretkeyrandomizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate one secret")
    generate_parser.add_argument("--preset", default="jwt", help="Preset key, for example jwt or aes-256")
    generate_parser.add_argument("--bytes", dest="byte_length", type=int, help="Byte or character length")
    generate_parser.add_argument("--encoding", help="hex, base64, base64url, ascii-safe, custom-charset, uuid-v4")
    generate_parser.add_argument("--env", dest="env_name", help="ENV variable name")
    generate_parser.add_argument("--format", dest="output_format", default="env", help="plain, env, or json")
    generate_parser.add_argument("--prefix", default=None)
    generate_parser.add_argument("--suffix", default=None)
    generate_parser.add_argument("--custom-charset", default=None)

    bulk_parser = subparsers.add_parser("bulk", help="Generate multiple presets")
    bulk_parser.add_argument("--preset", action="append", required=True, help="Preset key. Repeat for multiple.")
    bulk_parser.add_argument("--format", dest="output_format", default="env", help="env, json, or plain")

    template_parser = subparsers.add_parser("template", help="Generate a template pack")
    template_parser.add_argument("--template", required=True, help="Template key, for example web_api or django")
    template_parser.add_argument("--format", dest="output_format", default="env", help="env, json, or plain")

    subparsers.add_parser("list-presets", help="List presets and template packs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        request = request_from_preset(
            args.preset,
            output_format=args.output_format,
            encoding=args.encoding,
            byte_length=args.byte_length,
            env_name=args.env_name,
            prefix=args.prefix,
            suffix=args.suffix,
            custom_charset=args.custom_charset,
        )
        print(_format_single(generate_from_request(request), request.output_format))
        return 0

    if args.command == "bulk":
        requests = [request_from_preset(preset_key, output_format=args.output_format) for preset_key in args.preset]
        print(_format_batch(generate_batch("Bulk .env", requests), args.output_format))
        return 0

    if args.command == "template":
        print(_format_batch(generate_template_pack(args.template, output_format=args.output_format), args.output_format))
        return 0

    if args.command == "list-presets":
        _print_catalog()
        return 0

    parser.error("Unsupported command.")
    return 2


def _format_single(generated: GeneratedSecret, output_format: str) -> str:
    normalized = normalize_output_format(output_format)
    if normalized == "plain":
        return format_plain(generated.value)
    if normalized == "env":
        return format_env(generated.env_name, generated.value)
    if normalized == "json":
        return format_generated_json(generated)
    raise ValueError("Unsupported output format.")


def _format_batch(batch: GenerationBatch, output_format: str) -> str:
    normalized = normalize_output_format(output_format)
    if normalized == "plain":
        return "\n".join(generated.value for generated in batch.secrets)
    if normalized == "env":
        return format_env_block(batch.secrets)
    if normalized == "json":
        return format_json_array(batch)
    raise ValueError("Unsupported output format.")


def _print_catalog() -> None:
    print("Presets:")
    for preset in PRESETS.values():
        print(f"  {preset.key}: {preset.name} [{preset.category}] -> {preset.env_name}")
    print("")
    print("Template packs:")
    for key, (name, preset_keys) in TEMPLATE_PACKS.items():
        print(f"  {key}: {name} ({', '.join(preset_keys)})")


if __name__ == "__main__":
    raise SystemExit(main())
