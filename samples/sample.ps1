# Preview file: PowerShell
param(
    [string]$Name = 'World',
    [int]$Count = 3
)

function Get-Greeting {
    param([string]$Who)
    return "Hello, $Who!"
}

foreach ($i in 1..$Count) {
    Write-Host (Get-Greeting -Who $Name) -ForegroundColor Magenta
}
$items = Get-ChildItem -Path $env:TEMP | Where-Object { $_.Length -gt 1KB }
