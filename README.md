# SecretKeyRandomizer

SecretKeyRandomizer is a small Python desktop utility for generating developer
secrets such as JWT secrets, API keys, webhook signing secrets, AES-256 keys,
HMAC secrets, session secrets, CSRF secrets, salts, and random tokens.

It uses Python's cryptographically secure randomness APIs and keeps the secret
generation core separate from the PySide6 interface.

## Features

- PySide6 desktop UI with Single, Bulk .env, and Template Pack workflows
- CSPRNG-backed secret generation
- Built-in presets for common developer and framework secrets
- Hex, Base64, Base64URL, ASCII-safe, custom charset, and UUID-v4 outputs
- Plain value, `.env`, and JSON output formats
- Bulk `.env` and template pack generation
- Masked output by default with manual reveal
- Prefix and suffix support
- Entropy estimate and security level display
- Manual copy to clipboard with 10, 30, or 60 second auto-clear
- No telemetry, no network access, no database, no secret history
- pytest test coverage for the core behavior
- Portable Windows EXE release with SHA256 checksum

## Security Model

This project is designed for an open source security model. Security does not
depend on hidden source code, hidden algorithms, hidden presets, or closed build
steps.

SecretKeyRandomizer generates high-entropy secrets using cryptographically
secure randomness. Its security does not rely on hidden algorithms or closed
source code.

Secrets generated with sufficient entropy using a cryptographically secure
random source are computationally infeasible to brute-force in practice.

Important limits:

- Generated secrets are not stored by the application.
- Clipboard is not secure storage.
- This is a secret generator, not a secret manager.
- Users are responsible for storing generated secrets safely.
- Malware, keyloggers, screen capture tools, unsafe `.env` handling, logs, and
  accidental commits are outside this tool's protection boundary.

## Installation

For end users, download `SecretKeyRandomizer.exe` from GitHub Releases and run
it directly. The release `.exe` is packaged with PyInstaller and includes the
Python runtime and required Python packages. Python, PySide6, pytest, and
PyInstaller do not need to be installed separately to run the release asset.

For developers running from source, Python 3.12 or newer is recommended.

```powershell
.\scripts\setup-dev.ps1
```

Manual setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The Desktop App

```powershell
python app/main.py
```

## Optional CLI

```powershell
python -m app.cli.commands generate --preset jwt --format env
python -m app.cli.commands generate --preset aes-256 --encoding hex --format env
python -m app.cli.commands generate --bytes 32 --encoding base64url --env JWT_SECRET --format json
python -m app.cli.commands bulk --preset jwt --preset api-key --preset webhook --format env
python -m app.cli.commands template --template django --format env
python -m app.cli.commands list-presets
```

## Presets

| Preset | ENV name | Default bytes | Encoding |
| --- | --- | ---: | --- |
| JWT Secret | `JWT_SECRET` | 32 | Base64URL |
| API Key | `API_KEY` | 32 | Base64URL with `sk_` prefix |
| Webhook Secret | `WEBHOOK_SECRET` | 32 | Base64URL with `whsec_` prefix |
| AES-256 Key | `ENCRYPTION_KEY` | 32 | Hex |
| HMAC-SHA256 Secret | `HMAC_SECRET` | 32 | Base64URL |
| Session Secret | `SESSION_SECRET` | 32 | Base64URL |
| CSRF Secret | `CSRF_SECRET` | 32 | Base64URL |
| Refresh Token Secret | `REFRESH_TOKEN_SECRET` | 32 | Base64URL |
| Database Encryption Key | `DATABASE_ENCRYPTION_KEY` | 32 | Hex |
| Salt | `SALT` | 16 | Hex |
| Random Token | `RANDOM_TOKEN` | 32 | Base64URL |
| Django SECRET_KEY | `DJANGO_SECRET_KEY` | 50 | ASCII-safe |
| Laravel APP_KEY | `APP_KEY` | 32 | Base64 |
| Rails SECRET_KEY_BASE | `SECRET_KEY_BASE` | 64 | Hex |
| NextAuth Secret | `NEXTAUTH_SECRET` | 32 | Base64URL |
| OAuth Client Secret | `OAUTH_CLIENT_SECRET` | 32 | Base64URL |

## Entropy Levels

| Entropy bits | Level |
| ---: | --- |
| 0-63 | Weak |
| 64-127 | Medium |
| 128-255 | Strong |
| 256+ | Very Strong |

Prefix and suffix values are treated as public metadata and are not counted in
entropy estimates.

## Repository Safety

Do not commit real generated secrets. Use placeholders in examples:

```env
JWT_SECRET=<generate-with-secretkeyrandomizer>
API_KEY=<generate-with-secretkeyrandomizer>
WEBHOOK_SECRET=<generate-with-secretkeyrandomizer>
ENCRYPTION_KEY=<generate-with-secretkeyrandomizer>
```

## Build A Windows EXE

```powershell
python build_exe.py
```

Build the local release files with a checksum:

```powershell
.\scripts\build-release.ps1
```

Equivalent PyInstaller command:

```powershell
pyinstaller --noconfirm --onefile --windowed --name SecretKeyRandomizer app/main.py
```

Expected output:

```text
dist/SecretKeyRandomizer.exe
dist/SecretKeyRandomizer.exe.sha256
```

## GitHub Release

Push a version tag to build and publish a Windows release automatically:

```powershell
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

The release workflow runs tests, builds `SecretKeyRandomizer.exe`, creates a
SHA256 checksum, creates a source zip, and attaches all release files to the
GitHub Release.

Runtime notes for Windows users are in `docs/windows-install.md`.

## Run Tests

```powershell
pytest
```

## License

MIT License.
