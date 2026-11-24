$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    uv venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv pip install --python .venv/Scripts/python.exe -r requirements.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& .venv/Scripts/python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
