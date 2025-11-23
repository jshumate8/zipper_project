<#
Create and populate a Python virtual environment for development.

Usage (PowerShell):
  # from repo root
  .\scripts\dev_setup.ps1            # install pytest only
  .\scripts\dev_setup.ps1 -IncludeOptional  # also install optional packages from requirements.txt

This script will:
- create `.venv` if missing
- use the venv python to upgrade `pip`, `setuptools`, and `wheel`
- install `pytest` (and optional extras if requested)

Note: To activate the venv for interactive use, run:
  . .\.venv\Scripts\Activate.ps1
#>

[CmdletBinding()]
param(
    [switch]$IncludeOptional
)

function Fail($msg) { Write-Error $msg; exit 1 }

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Fail "Python is not available on PATH. Install Python 3.8+ and try again."
}

$venvPath = Join-Path -Path (Get-Location) -ChildPath '.venv'
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..."
    python -m venv $venvPath
} else {
    Write-Host ".venv already exists — reusing it."
}

$venvPython = Join-Path $venvPath 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Fail "Expected venv python not found at $venvPython"
}

Write-Host "Upgrading packaging tools in venv..."
& $venvPython -m pip install --upgrade pip setuptools wheel

Write-Host "Installing test tooling (pytest)..."
& $venvPython -m pip install pytest

if ($IncludeOptional) {
    if (-not (Test-Path 'requirements.txt')) {
        Write-Warning "requirements.txt not found — skipping optional install"
    } else {
        Write-Host "Installing optional requirements from requirements.txt..."
        & $venvPython -m pip install -r requirements.txt
    }
}

Write-Host "Done. To activate the venv in this shell run:`n. .\.venv\Scripts\Activate.ps1"
Write-Host "Then run: python -m pytest -q"
