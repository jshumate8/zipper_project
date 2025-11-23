<#
PowerShell release helper script.

Usage (PowerShell):
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\scripts\release.ps1 -Tag v0.1.1 -Message "Release v0.1.1" -Push

This script will:
- verify `git` is available
- check the working tree is clean (unless -AllowDirty)
- create an annotated tag
- push the tag (if -Push)
- (optionally) create a GitHub release via `gh` if installed (if -CreateGhRelease)

It does NOT push tags or create releases unless you pass `-Push` and/or `-CreateGhRelease`.
#>

param(
    [Parameter(Mandatory=$true)] [string]$Tag,
    [Parameter(Mandatory=$false)] [string]$Message = "Release $Tag",
    [switch]$Push,
    [switch]$CreateGhRelease,
    [switch]$AllowDirty
)

function Fail($msg) { Write-Error $msg; exit 1 }

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "git is not available in PATH. Install git and try again."
}

# Check we are in a git repo
try {
    $inside = git rev-parse --is-inside-work-tree 2>$null
} catch {
    Fail "Not inside a git repository. Run this from the repository root."
}

# Check working tree
if (-not $AllowDirty) {
    $status = git status --porcelain
    if ($status) {
        Fail "Working tree is dirty. Commit or stash changes, or pass -AllowDirty to continue.\nStatus:\n$status"
    }
}

# Create annotated tag
Write-Host "Creating annotated tag $Tag..."
$tagCmd = "git tag -a $Tag -m \"$Message\""
$tagResult = & git tag -a $Tag -m "$Message" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create tag: $tagResult"
    exit $LASTEXITCODE
}
Write-Host "Tag $Tag created locally."

if ($Push) {
    Write-Host "Pushing tag $Tag to origin..."
    $pushResult = & git push origin $Tag 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push tag: $pushResult"
        exit $LASTEXITCODE
    }
    Write-Host "Tag pushed."
}

if ($CreateGhRelease) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Warning "GitHub CLI 'gh' not found. Skipping GitHub release creation."
    } else {
        Write-Host "Creating GitHub release for $Tag using gh..."
        $notesPath = Join-Path -Path (Get-Location) -ChildPath 'RELEASE_NOTES.md'
        if (-not (Test-Path $notesPath)) {
            Write-Warning "RELEASE_NOTES.md not found in repository root. Creating release without notes."
            $ghRes = gh release create $Tag --title $Tag 2>&1
        } else {
            $ghRes = gh release create $Tag --title $Tag --notes-file $notesPath 2>&1
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Error "gh release command failed: $ghRes"
            exit $LASTEXITCODE
        }
        Write-Host "GitHub release created for $Tag."
    }
}

Write-Host "Done."
