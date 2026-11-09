# =============================================================================
# Dusk Rose for PuTTY - install on Windows
#
# WHAT IT DOES   Sets PuTTY's colours to Dusk Rose (or Dusk Rose Light) for new
#                sessions AND every session you've already saved. Also turns
#                off cursor blinking and switches the font to Consolas 12pt
#                with ClearType smoothing (easier to read than the default).
# SAFE TO RUN    Backs up all your PuTTY settings first to a .reg file in your
#                user folder. To undo, double-click that backup file.
# YOU NEED       PuTTY on Windows. Close any open PuTTY windows first.
# HOW TO RUN     In PowerShell (dark version):
#                  irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install-putty.ps1 | iex
#                For the light version, download this file and run:
#                  .\install-putty.ps1 -Variant Light
#                To change colours only and keep your current font:
#                  .\install-putty.ps1 -KeepFont
# AFTERWARDS     Open PuTTY and load a session - it's already themed.
#                (PuTTY can't follow Windows light/dark mode, so pick one.)
# =============================================================================
param(
    [ValidateSet('Dark', 'Light')]
    [string]$Variant = 'Dark',
    [switch]$KeepFont
)
$ErrorActionPreference = 'Stop'

$Repo     = 'DCodeAus/dusk-rose-theme'
$RegFile  = if ($Variant -eq 'Light') { 'dusk-rose-light.reg' } else { 'dusk-rose.reg' }
$PuttyKey = 'HKCU:\Software\SimonTatham\PuTTY'
$Sessions = "$PuttyKey\Sessions"

# 1. Back up everything PuTTY has saved, so this can be undone.
$Backup = Join-Path $HOME ("putty-backup-{0:yyyy-MM-dd-HHmm}.reg" -f (Get-Date))
if (Test-Path $PuttyKey) {
    reg export 'HKCU\Software\SimonTatham\PuTTY' $Backup /y | Out-Null
    Write-Host "Backed up your PuTTY settings to $Backup"
}

# 2. Get the theme file: use the copy next to this script if there is one,
#    otherwise download it from GitHub.
$Local = if ($PSScriptRoot) { Join-Path $PSScriptRoot "putty\$RegFile" } else { $null }
if ($Local -and (Test-Path $Local)) {
    $Text = Get-Content $Local -Raw
} else {
    $Text = (Invoke-WebRequest "https://raw.githubusercontent.com/$Repo/main/putty/$RegFile" -UseBasicParsing).Content
}

# 3. Read the settings out of the .reg text (lines like "Colour0"="29,30,38"
#    or "FontHeight"=dword:0000000c) so this script and the .reg file can
#    never disagree.
$Values = [ordered]@{}
foreach ($Line in $Text -split "`r?`n") {
    if ($Line -match '^"([^"]+)"="([^"]*)"$') {
        $Values[$Matches[1]] = @{ Type = 'String'; Data = $Matches[2] }
    } elseif ($Line -match '^"([^"]+)"=dword:([0-9a-fA-F]{8})$') {
        $Values[$Matches[1]] = @{ Type = 'DWord'; Data = [Convert]::ToInt32($Matches[2], 16) }
    }
}
if ($KeepFont) {
    foreach ($Name in 'Font', 'FontIsBold', 'FontCharSet', 'FontHeight', 'FontQuality') { $Values.Remove($Name) }
}

# 4. Apply to "Default Settings" (used for new sessions) plus every saved session.
if (-not (Test-Path "$Sessions\Default%20Settings")) {
    New-Item -Path "$Sessions\Default%20Settings" -Force | Out-Null
}
$Targets = Get-ChildItem $Sessions
foreach ($Session in $Targets) {
    foreach ($Name in $Values.Keys) {
        Set-ItemProperty -Path $Session.PSPath -Name $Name -Value $Values[$Name].Data -Type $Values[$Name].Type
    }
    # Session names are stored URL-encoded (spaces as %20); show them normally.
    Write-Host ("  themed: " + [Uri]::UnescapeDataString($Session.PSChildName))
}
Write-Host "Done - Dusk Rose $Variant applied to $($Targets.Count) PuTTY session(s)."
