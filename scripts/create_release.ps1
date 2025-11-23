# Create a GitHub release with Windows executables
# Usage: .\scripts\create_release.ps1 -Version v0.1.1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host "=== Zipper Release Creator ===" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow

# Check if we're in the repo root
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "Must run from repository root"
}

# Build executables unless skipped
if (-not $SkipBuild) {
    Write-Host "`nBuilding executables..." -ForegroundColor Green
    
    # Activate venv
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & .venv\Scripts\Activate.ps1
    }
    
    # Install PyInstaller
    python -m pip install --quiet pyinstaller
    
    # Build GUI
    Write-Host "Building GUI executable..."
    pyinstaller --onefile --noconsole --name zipper-gui build\run_zipper_gui.py --clean
    
    # Build CLI
    Write-Host "Building CLI executable..."
    pyinstaller --onefile --name zipper-cli build\run_zipper_cli.py --clean
    
    Write-Host "Done!" -ForegroundColor Green
}
else {
    Write-Host "`nSkipping build" -ForegroundColor Yellow
}

# Verify executables exist
if (-not (Test-Path "dist\zipper-gui.exe")) {
    Write-Error "GUI executable not found in dist/"
}
if (-not (Test-Path "dist\zipper-cli.exe")) {
    Write-Error "CLI executable not found in dist/"
}

# Get file sizes
$guiSize = (Get-Item "dist\zipper-gui.exe").Length / 1MB
$cliSize = (Get-Item "dist\zipper-cli.exe").Length / 1MB
Write-Host "`nExecutable sizes:"
Write-Host "  zipper-gui.exe: $([math]::Round($guiSize, 2)) MB"
Write-Host "  zipper-cli.exe: $([math]::Round($cliSize, 2)) MB"

# Create git tag
Write-Host "`nCreating git tag '$Version'..." -ForegroundColor Green
git tag -a $Version -m "Release $Version"

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Push the tag to GitHub:"
Write-Host "   git push origin $Version" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Create a GitHub release:"
Write-Host "   - Go to: https://github.com/jshumate8/zipper_project/releases/new"
Write-Host "   - Choose tag: $Version"
Write-Host "   - Upload dist\zipper-gui.exe and dist\zipper-cli.exe"
Write-Host "   - Publish release"
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
