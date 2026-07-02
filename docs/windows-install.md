# Windows Install And Runtime Notes

## For End Users

Use the GitHub Release asset:

```text
SecretKeyRandomizer.exe
```

The release `.exe` is packaged with PyInstaller as a one-file Windows
application. It includes the Python runtime and required Python packages inside
the executable bundle.

End users do not need to install:

- Python
- PySide6
- pytest
- PyInstaller

On first launch, Windows SmartScreen may warn because the executable is not code
signed. This is a publisher trust warning, not a missing dependency. Code signing
can be added later with a Windows code-signing certificate.

## For Developers

Developers running from source should install Python 3.12+ and project
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

Manual equivalent:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the app:

```powershell
python app/main.py
```

Build the `.exe` locally:

```powershell
python build_exe.py
```
