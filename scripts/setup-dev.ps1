$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.12+ is required for source development."
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Development environment is ready."
Write-Host "Run: .\.venv\Scripts\python.exe app/main.py"
