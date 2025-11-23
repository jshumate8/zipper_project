<#
.SYNOPSIS
    Create a GitHub release with Windows executables

.DESCRIPTION
    This script helps prepare a release by:
    1. Building fresh executables
    2. Creating a git tag
    3. Providing commands to create a GitHub release with attachments

.PARAMETER Version
    Version tag (e.g., "v0.1.1")

.PARAMETER SkipBuild
    Skip rebuilding executables (use existing dist/ files)

.EXAMPLE
    .\scripts\create_release.ps1 -Version v0.1.1
#>

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
    Write-Error "Must run from repository root (where pyproject.toml exists)"
}

# Activate venv if it exists
$venvActivate = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $venvActivate
}

# Build executables unless skipped
if (-not $SkipBuild) {
    Write-Host "`nBuilding executables..." -ForegroundColor Green
    
    # Install PyInstaller if needed
    python -m pip install --quiet pyinstaller
    
    # Build GUI exe
    Write-Host "Building GUI executable..."
    pyinstaller --onefile --noconsole --name zipper-gui build\run_zipper_gui.py --clean
    
    # Build CLI exe
    Write-Host "Building CLI executable..."
    pyinstaller --onefile --name zipper-cli build\run_zipper_cli.py --clean
    
    Write-Host "✓ Executables built successfully" -ForegroundColor Green
} else {
    Write-Host "`nSkipping build (using existing executables)" -ForegroundColor Yellow
}

# Verify executables exist
if (-not (Test-Path "dist\zipper-gui.exe") -or -not (Test-Path "dist\zipper-cli.exe")) {
    Write-Error "Executables not found in dist/. Run without -SkipBuild or build manually."
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
Write-Host @"

1. Push the tag to GitHub:
   git push origin $Version

2. Create a GitHub release (choose one method):

   METHOD A - GitHub Web UI:
   - Go to: https://github.com/jshumate8/zipper_project/releases/new
   - Choose tag: $Version
   - Title: $Version
   - Upload these files as release assets:
     * dist\zipper-gui.exe
     * dist\zipper-cli.exe
   - Click "Publish release"

   METHOD B - GitHub CLI (gh):
   gh release create $Version dist\zipper-gui.exe dist\zipper-cli.exe \
       --title "$Version" \
       --notes "See CHANGELOG.md for details"

3. Verify the release:
   https://github.com/jshumate8/zipper_project/releases

"@ -ForegroundColor White

Write-Host "✓ Release preparation complete!" -ForegroundColor Green
