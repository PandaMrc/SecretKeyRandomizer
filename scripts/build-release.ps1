$ErrorActionPreference = "Stop"

& .\.venv\Scripts\python.exe build_exe.py

$exePath = "dist\SecretKeyRandomizer.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Build did not create $exePath"
}

$hash = Get-FileHash -Algorithm SHA256 $exePath
"$($hash.Hash.ToLower())  SecretKeyRandomizer.exe" | Set-Content -Encoding ascii "dist\SecretKeyRandomizer.exe.sha256"

Write-Host "Release files are ready:"
Write-Host "  dist\SecretKeyRandomizer.exe"
Write-Host "  dist\SecretKeyRandomizer.exe.sha256"
