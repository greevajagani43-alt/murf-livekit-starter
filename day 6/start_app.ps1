# Day 6 — Start All Services (Windows PowerShell)
# Starts: backend agent + trigger server + frontend dev server
#
# Usage:
#   .\start_app.ps1
#
# Before running:
#   1. Fill in day 6\backend\.env.local  (especially LIVEKIT_SIP_TRUNK_ID)
#   2. Fill in day 6\frontend\.env.local
#   3. Run:  cd "day 6\backend" && uv sync
#   4. Run:  cd "day 6\frontend" && pnpm install

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Saathi — Day 6: Outbound Calls" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Start the LiveKit agent ─────────────────────────────────────────────
Write-Host "[1/3] Starting Saathi voice agent..." -ForegroundColor Yellow
$backendDir = Join-Path $root "backend"
$agentProc = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendDir'; uv run python src/agent.py dev"
) -PassThru

Start-Sleep -Seconds 3

# ── 2. Start the trigger server (FastAPI on port 8001) ────────────────────
Write-Host "[2/3] Starting outbound trigger server on http://localhost:8001 ..." -ForegroundColor Yellow
$triggerProc = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendDir'; uv run uvicorn src.trigger_server:app --host 0.0.0.0 --port 8001 --reload"
) -PassThru

Start-Sleep -Seconds 2

# ── 3. Start the Next.js frontend ─────────────────────────────────────────
Write-Host "[3/3] Starting frontend on http://localhost:3000 ..." -ForegroundColor Yellow
$frontendDir = Join-Path $root "frontend"
$frontendProc = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$frontendDir'; pnpm dev"
) -PassThru

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "  Agent:          http://localhost:7880 (LiveKit)" -ForegroundColor White
Write-Host "  Trigger Server: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Frontend:       http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  To trigger an outbound call:" -ForegroundColor White
Write-Host "  uv run python src/trigger_call.py --number +91XXXXXXXXXX --name 'Your Name'" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Keep window alive
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray
try {
    Wait-Process -Id $agentProc.Id
} catch {
    # Cleanup
    Stop-Process -Id $agentProc.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $triggerProc.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
}
