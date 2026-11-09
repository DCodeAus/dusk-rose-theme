# =============================================================================
# Dusk Rose for PuTTY - install on Windows (no admin rights needed)
#
# WHAT IT DOES   Sets PuTTY's colours to Dusk Rose (or Dusk Rose Light) for new
#                sessions AND every session you've already saved. Also turns
#                off cursor blinking and switches the font to Consolas 12pt
#                with ClearType smoothing (easier to read than the default).
# NO ADMIN       PuTTY keeps its settings in your own part of the registry
#                (HKEY_CURRENT_USER), so this only touches your user account.
#                It doesn't use reg.exe or regedit, which work PCs often block.
# SAFE TO RUN    First saves your current PuTTY colour/font settings to
#                putty-backup-<date>.reg in your user folder. To undo:
#                  .\install-putty.ps1 -Restore "$HOME\putty-backup-<date>.reg"
#                (or double-click the backup, if your PC allows .reg files).
# YOU NEED       PuTTY installed normally (not the portable version, which
#                keeps settings in a file). Close any open PuTTY windows first.
# HOW TO RUN     In PowerShell (dark version):
#                  irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install-putty.ps1 | iex
#                With options (light version and/or keep your current font):
#                  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install-putty.ps1))) -Variant Light -KeepFont
#                If you downloaded this file and Windows says "running scripts
#                is disabled", use (affects this one run only, no admin):
#                  powershell -ExecutionPolicy Bypass -File .\install-putty.ps1
# AFTERWARDS     Open PuTTY and load a session - it's already themed.
#                (PuTTY can't follow Windows light/dark mode, so pick one.)
# =============================================================================
# Printing progress to the screen is the point of an installer, so the
# "avoid Write-Host" style warning doesn't apply here.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '', Justification = 'Interactive installer output')]
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Dark', 'Light')]
    [string]$Variant = 'Dark',
    [switch]$KeepFont,
    [string]$Restore
)
$ErrorActionPreference = 'Stop'

$Repo     = 'DCodeAus/dusk-rose-theme'
$Sessions = 'HKCU:\Software\SimonTatham\PuTTY\Sessions'
$RegRoot  = 'HKEY_CURRENT_USER\Software\SimonTatham\PuTTY\Sessions'

# --- Helpers ----------------------------------------------------------------
# These read and write .reg text with plain PowerShell (no .NET calls), so they
# also work on locked-down PCs that restrict what PowerShell can do.

function ConvertFrom-RegText([string]$Text) {
    # Turns .reg text into a list of settings: which session, name, type, value.
    $Section = $null
    foreach ($Line in $Text -split "`r?`n") {
        if ($Line -match '^\[HKEY_CURRENT_USER\\Software\\SimonTatham\\PuTTY\\Sessions\\(.+)\]$') {
            $Section = $Matches[1]
        } elseif ($Section -and $Line -match '^"([^"]+)"="((?:[^"\\]|\\.)*)"$') {
            # .reg strings escape \ and " with a backslash - undo that.
            $Data = $Matches[2] -replace '\\(.)', '$1'
            [pscustomobject]@{ Session = $Section; Name = $Matches[1]; Type = 'String'; Data = $Data }
        } elseif ($Section -and $Line -match '^"([^"]+)"=dword:([0-9a-fA-F]{8})$') {
            [pscustomobject]@{ Session = $Section; Name = $Matches[1]; Type = 'DWord'; Data = [int]('0x' + $Matches[2]) }
        }
    }
}

function ConvertTo-RegLine([string]$Name, $Value) {
    # One setting as a .reg line, e.g. "Colour0"="29,30,38" or "FontHeight"=dword:0000000c
    if ($Value -is [int]) { return ('"{0}"=dword:{1:x8}' -f $Name, $Value) }
    $Escaped = ([string]$Value).Replace('\', '\\').Replace('"', '\"')
    return ('"{0}"="{1}"' -f $Name, $Escaped)
}

function Set-PuttySetting {
    # Writes settings into the registry, creating a session key if it's missing.
    # Run the script with -WhatIf to see what would change without changing it.
    [CmdletBinding(SupportsShouldProcess)]
    param($Settings)
    foreach ($S in $Settings) {
        $Path = "$Sessions\$($S.Session)"
        if (-not $PSCmdlet.ShouldProcess(($S.Session -replace '%20', ' '), "set $($S.Name) = $($S.Data)")) { continue }
        if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
        Set-ItemProperty -Path $Path -Name $S.Name -Value $S.Data -Type $S.Type
    }
}

# --- Undo mode: put a backup back -------------------------------------------
if ($Restore) {
    $Settings = @(ConvertFrom-RegText (Get-Content $Restore -Raw))
    Set-PuttySetting $Settings
    Write-Host "Restored $($Settings.Count) setting(s) from $Restore"
    return
}

# --- 1. Get the theme -------------------------------------------------------
# Use the copy next to this script if there is one, otherwise download it.
$RegFile = if ($Variant -eq 'Light') { 'dusk-rose-light.reg' } else { 'dusk-rose.reg' }
$Local = if ($PSScriptRoot) { Join-Path $PSScriptRoot "putty\$RegFile" } else { $null }
if ($Local -and (Test-Path $Local)) {
    $Text = Get-Content $Local -Raw
} else {
    $Text = (Invoke-WebRequest "https://raw.githubusercontent.com/$Repo/main/putty/$RegFile" -UseBasicParsing).Content
}
# The theme file only lists "Default Settings"; we copy those values everywhere.
$Theme = @(ConvertFrom-RegText $Text)
if ($KeepFont) {
    $Theme = @($Theme | Where-Object { $_.Name -notlike 'Font*' })
}
if ($Theme.Count -eq 0) { throw "Couldn't read any settings from $RegFile." }

# --- 2. Work out which sessions to theme -------------------------------------
# "Default Settings" (used for new sessions) plus every saved session.
$Targets = @('Default%20Settings')
if (Test-Path $Sessions) {
    $Targets += @(Get-ChildItem $Sessions | ForEach-Object { $_.PSChildName } |
                  Where-Object { $_ -ne 'Default%20Settings' })
}

# --- 3. Back up the settings we're about to change ---------------------------
# Only the values this script touches, so restoring can't disturb anything else.
$Backup = Join-Path $HOME ('putty-backup-{0:yyyy-MM-dd-HHmmss}.reg' -f (Get-Date))
$Lines = @('Windows Registry Editor Version 5.00', '',
           '; Dusk Rose installer backup. Undo with:',
           "; .\install-putty.ps1 -Restore `"$Backup`"", '')
foreach ($Session in $Targets) {
    $Path = "$Sessions\$Session"
    if (-not (Test-Path $Path)) { continue }   # nothing to back up yet
    $Current = Get-ItemProperty -Path $Path
    $Lines += "[$RegRoot\$Session]"
    foreach ($Name in ($Theme.Name | Select-Object -Unique)) {
        if ($null -ne $Current.$Name) { $Lines += ConvertTo-RegLine $Name $Current.$Name }
    }
    $Lines += ''
}
Set-Content -Path $Backup -Value $Lines -Encoding Unicode
Write-Host "Backed up your current PuTTY settings to $Backup"

# --- 4. Apply the theme -------------------------------------------------------
foreach ($Session in $Targets) {
    Set-PuttySetting @($Theme | ForEach-Object {
        [pscustomobject]@{ Session = $Session; Name = $_.Name; Type = $_.Type; Data = $_.Data }
    })
    # Session names are stored with spaces as %20; show them normally.
    Write-Host ('  themed: ' + ($Session -replace '%20', ' '))
}
Write-Host "Done - Dusk Rose $Variant applied to $($Targets.Count) PuTTY session(s)."
Write-Host "To undo: .\install-putty.ps1 -Restore `"$Backup`""
