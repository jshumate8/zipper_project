<#
Install Chocolatey helper script.

Usage (run in an elevated PowerShell prompt):
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\scripts\install_choco.ps1

This script performs safety checks and then runs the official Chocolatey install script.
It does not push changes or require anything from this repo.
#>

function Is-Administrator {
    $current = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Is-Administrator)) {
    Write-Error "This script must be run from an elevated PowerShell (Run as Administrator)."
    exit 1
}

Write-Host "Installing Chocolatey..." -ForegroundColor Cyan

try {
    # Ensure TLS 1.2 (required for secure downloads)
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $installScriptUrl = 'https://community.chocolatey.org/install.ps1'
    Write-Host "Downloading installer from $installScriptUrl" -ForegroundColor Yellow

    $script = (New-Object System.Net.WebClient).DownloadString($installScriptUrl)
    if (-not $script) {
        Write-Error "Failed to download the Chocolatey install script."
        exit 2
    }

    Write-Host "Executing installer..." -ForegroundColor Yellow
    Invoke-Expression $script

    Write-Host "Chocolatey installation finished. Verify with 'choco --version' after closing and reopening terminals." -ForegroundColor Green
} catch {
    Write-Error "Installation failed: $_"
    exit 3
}
