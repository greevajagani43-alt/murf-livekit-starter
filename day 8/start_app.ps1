# Windows PowerShell launcher for Day 8 Voice Agent Performance Dashboard
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Starting Day 8 — Voice Agent Performance Dashboard" -ForegroundColor Green
Write-Host " Track: Local Commerce | Murf Falcon TTS | Real SQLite Metrics" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend Agent
Write-Host "`n[1/3] Starting Backend Voice Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; uv sync; uv run python src/agent.py dev"

# 2. Start Dashboard REST API Server (Port 8003)
Write-Host "[2/3] Starting Dashboard REST API Server (Port 8003)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; uv run python src/dashboard_server.py"

# 3. Start Frontend Dashboard UI (Port 3000)
Write-Host "[3/3] Starting Frontend Dashboard UI (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; pnpm install; pnpm dev"

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host " Day 8 Services Started Successfully!" -ForegroundColor Green
Write-Host " Dashboard UI:     http://localhost:3000" -ForegroundColor Yellow
Write-Host " Dashboard REST API: http://localhost:8003/api/dashboard/stats" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
