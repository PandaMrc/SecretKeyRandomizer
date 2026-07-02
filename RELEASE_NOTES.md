# SecretKeyRandomizer v1.0.0

First complete public release.

## Included

- Single secret generation
- Bulk `.env` generation
- Template packs for Web API, Auth/JWT, Encryption, Django, Laravel, Rails, and Next/Auth
- Presets for common application, framework, signing, encryption, and token secrets
- Hex, Base64, Base64URL, ASCII-safe, custom charset, and UUID-v4 outputs
- Plain value, `.env`, and JSON output formats
- Masked output by default with manual reveal
- Clipboard copy controls with 10, 30, or 60 second auto-clear
- No telemetry, no network access, no database, no secret history, and no secret persistence
- Portable Windows `.exe` release through PyInstaller
- SHA256 checksum for the Windows executable

## Windows Download

Download `SecretKeyRandomizer.exe` from the release assets and run it.

This is a portable one-file executable. End users do not need to install Python,
PySide6, pytest, PyInstaller, or any setup wizard.

## Verification

Use `SecretKeyRandomizer.exe.sha256` to verify the downloaded executable:

```powershell
Get-FileHash .\SecretKeyRandomizer.exe -Algorithm SHA256
```

Compare the hash with the value in `SecretKeyRandomizer.exe.sha256`.
