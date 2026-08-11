# Day 6 — Setup Script (Windows PowerShell)
# Run this ONCE before starting the app for the first time.
#
# Usage:
#   .\setup_day6.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Day 6 Setup - Outbound Calls" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# -- Backend setup --
$backendDir = Join-Path $root "day 6\backend"
Write-Host "[1/5] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location $backendDir
uv sync
Write-Host "  Backend deps installed." -ForegroundColor Green

Write-Host "[2/5] Downloading LiveKit model files..." -ForegroundColor Yellow
uv run python src/agent.py download-files
Write-Host "  Model files downloaded." -ForegroundColor Green

Write-Host "[3/5] Seeding demo customer profiles..." -ForegroundColor Yellow
uv run python src/seed_demo_user.py
Write-Host '  Demo users seeded (Rahul Sharma, Priya Patel).' -ForegroundColor Green

# -- Frontend setup --
$frontendDir = Join-Path $root "day 6\frontend"
Write-Host "[4/5] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location $frontendDir
pnpm install
Write-Host "  Frontend deps installed." -ForegroundColor Green

# -- Env file reminder --
Write-Host "[5/5] Checking .env.local files..." -ForegroundColor Yellow
$backendEnv = Join-Path $backendDir ".env.local"
$frontendEnv = Join-Path $frontendDir ".env.local"

if (-not (Test-Path $backendEnv)) {
    Copy-Item (Join-Path $backendDir ".env.example") $backendEnv
    Write-Host "  Created backend/.env.local from .env.example" -ForegroundColor Cyan
    Write-Host "  *** Please fill in your API keys! ***" -ForegroundColor Red
} else {
    Write-Host "  backend/.env.local already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "  1. Fill in LIVEKIT_SIP_TRUNK_ID in backend\.env.local" -ForegroundColor White
Write-Host "  2. Fill in TWILIO_* vars in backend\.env.local" -ForegroundColor White
Write-Host "  3. Run: .\start_app.ps1" -ForegroundColor Cyan
Write-Host '  4. Trigger a call: uv run python src/trigger_call.py --number +91XXXXXXXXXX' -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
