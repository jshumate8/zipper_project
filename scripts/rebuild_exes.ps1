<#
.SYNOPSIS
    Rebuild Windows executables using PyInstaller

.DESCRIPTION
    Quick script to rebuild both GUI and CLI executables.
    Activates venv and runs PyInstaller with appropriate flags.

.EXAMPLE
    .\scripts\rebuild_exes.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Rebuilding Zipper Executables ===" -ForegroundColor Cyan

# Check if we're in the repo root
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "Must run from repository root"
}

# Activate venv
$venvActivate = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $venvActivate
} else {
    Write-Warning "Virtual environment not found. Using system Python."
}

# Install PyInstaller if needed
Write-Host "Ensuring PyInstaller is installed..."
python -m pip install --quiet pyinstaller

# Clean previous builds
if (Test-Path "dist") {
    Write-Host "Cleaning previous build artifacts..."
    Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
}

# Build GUI exe
Write-Host "`nBuilding GUI executable..." -ForegroundColor Green
pyinstaller --onefile --noconsole --name zipper-gui build\run_zipper_gui.py

# Build CLI exe
Write-Host "`nBuilding CLI executable..." -ForegroundColor Green
pyinstaller --onefile --name zipper-cli build\run_zipper_cli.py

# Verify
if ((Test-Path "dist\zipper-gui.exe") -and (Test-Path "dist\zipper-cli.exe")) {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    
    $guiSize = (Get-Item "dist\zipper-gui.exe").Length / 1MB
    $cliSize = (Get-Item "dist\zipper-cli.exe").Length / 1MB
    
    Write-Host "`nExecutable sizes:"
    Write-Host "  zipper-gui.exe: $([math]::Round($guiSize, 2)) MB"
    Write-Host "  zipper-cli.exe: $([math]::Round($cliSize, 2)) MB"
    
    Write-Host "`nTest the executables:"
    Write-Host "  .\dist\zipper-gui.exe" -ForegroundColor Yellow
    Write-Host "  .\dist\zipper-cli.exe --help" -ForegroundColor Yellow
} else {
    Write-Error "Build failed - executables not found"
}
