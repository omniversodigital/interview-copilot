# PowerShell Launcher for Sovereign Interview Co-Pilot
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ⚡ SOVEREIGN INTERVIEW CO-PILOT ('THE CYRANO ENGINE') ⚡" -ForegroundColor Yellow
Write-Host "  Candidate: Jean Carlo Ferreira | Principal Systems Architect" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

python "$ScriptDir\start_copilot.py"
