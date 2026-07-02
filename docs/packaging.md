# Packaging

Install dependencies first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Build:

```powershell
python build_exe.py
```

The expected Windows artifact is:

```text
dist/SecretKeyRandomizer.exe
```
