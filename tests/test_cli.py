from __future__ import annotations

import json
import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.cli.commands", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_cli_generate_env() -> None:
    result = run_cli("generate", "--preset", "jwt", "--format", "env")

    assert result.stdout.startswith("JWT_SECRET=")


def test_cli_bulk_json() -> None:
    result = run_cli("bulk", "--preset", "jwt", "--preset", "api-key", "--format", "json")
    payload = json.loads(result.stdout)

    assert payload["name"] == "Bulk .env"
    assert [item["name"] for item in payload["secrets"]] == ["JWT_SECRET", "API_KEY"]


def test_cli_template_env() -> None:
    result = run_cli("template", "--template", "next-auth", "--format", "env")

    assert "NEXTAUTH_SECRET=" in result.stdout
    assert "JWT_SECRET=" in result.stdout


def test_cli_list_presets() -> None:
    result = run_cli("list-presets")

    assert "Presets:" in result.stdout
    assert "Template packs:" in result.stdout
    assert "django_secret_key" in result.stdout
