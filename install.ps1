# =============================================================================
# Dusk Rose - install / update on Windows
#
# WHAT IT DOES   Downloads the newest Dusk Rose release from GitHub and installs
#                it into VS Code. Run it again any time to update.
# YOU NEED       VS Code installed normally (the installer adds the `code` command).
# HOW TO RUN     In PowerShell:
#                irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install.ps1 | iex
# AFTERWARDS     In VS Code: Ctrl+Shift+P > "Developer: Reload Window".
#                Pick the theme with Ctrl+K Ctrl+T if it isn't already selected.
# =============================================================================
$ErrorActionPreference = 'Stop'

$Repo = 'DCodeAus/dusk-rose-theme'

# Stop early with a clear message if VS Code's command-line tool is missing.
if (-not (Get-Command code -ErrorAction SilentlyContinue)) {
    Write-Error "Can't find the 'code' command. Reinstall VS Code with 'Add to PATH' ticked, then run this again."
}

# Ask GitHub for the newest release and pick out the .vsix download link.
Write-Host 'Finding the latest Dusk Rose release...'
$Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
$Asset = $Release.assets | Where-Object { $_.name -like '*.vsix' } | Select-Object -First 1
if (-not $Asset) {
    Write-Error "Couldn't find a release to download. Check https://github.com/$Repo/releases"
}

# Download to the temp folder, install (--force replaces any older copy), tidy up.
$File = Join-Path $env:TEMP $Asset.name
Write-Host "Downloading $($Asset.name)..."
Invoke-WebRequest $Asset.browser_download_url -OutFile $File
code --install-extension $File --force
Remove-Item $File
Write-Host 'Done. Reload VS Code (Ctrl+Shift+P > Developer: Reload Window).'
