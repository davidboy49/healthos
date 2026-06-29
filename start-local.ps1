$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $root 'apps/api'
$webDir = Join-Path $root 'apps/web'
$apiPy = Join-Path $apiDir '.venv/Scripts/python.exe'

if (-not (Test-Path $apiPy)) {
  throw "Missing API virtual environment at $apiPy. Run the backend install first."
}

$apiCommand = "Set-Location '$apiDir'; & '$apiPy' -m uvicorn healthos_api.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile','-Command',$apiCommand) | Out-Null
Start-Process cmd.exe -WorkingDirectory $webDir -WindowStyle Hidden -ArgumentList @('/c','npm','run','dev') | Out-Null

Write-Host 'Started API on http://127.0.0.1:8000'
Write-Host 'Started web on http://127.0.0.1:3000'
