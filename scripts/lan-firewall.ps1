#Requires -RunAsAdministrator
param(
    [ValidateSet('enable', 'disable')]
    [string]$Action = 'enable'
)
$ErrorActionPreference = 'Stop'
$ruleName = 'xiangmu2-frontend-lan'
$rule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue

if ($Action -eq 'disable') {
    if ($rule) { Disable-NetFirewallRule -Name $ruleName | Out-Null }
    Write-Output 'xiangmu2 LAN firewall rule disabled.'
    exit 0
}

$nodePath = (Get-Command node.exe -ErrorAction Stop).Source
if ($rule) {
    Set-NetFirewallRule -Name $ruleName -Enabled True -Direction Inbound -Action Allow -Profile Any | Out-Null
    $rule | Get-NetFirewallPortFilter | Set-NetFirewallPortFilter -Protocol TCP -LocalPort 5174 | Out-Null
    $rule | Get-NetFirewallAddressFilter | Set-NetFirewallAddressFilter -RemoteAddress LocalSubnet | Out-Null
    $rule | Get-NetFirewallApplicationFilter | Set-NetFirewallApplicationFilter -Program $nodePath | Out-Null
} else {
    New-NetFirewallRule -Name $ruleName -DisplayName 'xiangmu2 frontend LAN (TCP 5174)' `
        -Direction Inbound -Action Allow -Enabled True -Profile Any `
        -Protocol TCP -LocalPort 5174 -RemoteAddress LocalSubnet -Program $nodePath | Out-Null
}
Write-Output 'Allowed xiangmu2 frontend TCP 5174 from LocalSubnet only.'
