"""Build a Windows executable with PyInstaller."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "SecretKeyRandomizer",
        "app/main.py",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
