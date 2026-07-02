# SecretKeyRandomizer v0.1.0

Initial MVP release.

## Included

- PySide6 desktop interface
- CSPRNG-backed secret generation
- Presets for JWT, API key, webhook, AES-256, HMAC, session, CSRF, refresh token, database encryption, salt, and random token use cases
- Hex, Base64, Base64URL, ASCII-safe, custom charset, and UUID-v4 outputs
- Plain text, `.env`, and JSON output formats
- Entropy and security level display
- Manual clipboard copy with optional auto-clear
- No telemetry, no network access, no database, and no secret history
- Windows `.exe` build through PyInstaller

## Windows Download

Download `SecretKeyRandomizer.exe` from the release assets and run it.

The `.exe` is built as a PyInstaller one-file application. End users do not need
to install Python, PySide6, pytest, or PyInstaller to run the release asset.

## Source Usage

Developers running from source need Python 3.12+ and the packages listed in
`requirements.txt`.
