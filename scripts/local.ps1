param(
    [ValidateSet('start', 'stop', 'status', 'check', 'redis')]
    [string]$Action = 'start'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot 'mature-evaluation-system-backend\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Create the project .venv and install requirements-local.txt first.' }
$env:PYTHONIOENCODING = 'utf-8'
& $pythonExe (Join-Path $PSScriptRoot 'local.py') $Action
exit $LASTEXITCODE
