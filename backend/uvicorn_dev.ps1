$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Python executable not found: $Python"
}

Set-Location $ProjectRoot

Write-Host "Starting AI Software Company backend..."
Write-Host "Reload is intentionally disabled."
Write-Host ""

& $Python -m uvicorn backend.app.main:app `
    --host 127.0.0.1 `
    --port 8010
