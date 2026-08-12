# Windows PowerShell launcher for Day 8 Voice Agent Performance Dashboard
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Starting Day 8 — Voice Agent Performance Dashboard" -ForegroundColor Green
Write-Host " Track: Local Commerce | Murf Falcon TTS | Real SQLite Metrics" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

$scriptPath = $PSScriptRoot

Write-Host ""
Write-Host "[1/3] Starting Backend Voice Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; uv sync; uv run python src/agent.py dev"

Write-Host "[2/3] Starting Dashboard REST API Server (Port 8003)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; uv run python src/dashboard_server.py"

Write-Host "[3/3] Starting Frontend Dashboard UI (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; pnpm dev"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host " Day 8 Services Started Successfully!" -ForegroundColor Green
Write-Host " Dashboard UI:       http://localhost:3000" -ForegroundColor Yellow
Write-Host " Dashboard REST API: http://localhost:8003/api/dashboard/stats" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
