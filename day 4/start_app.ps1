$ErrorActionPreference = "Stop"

function Test-CommandExists {
  param([string]$CommandName)
  return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandExists "uv")) {
  Write-Error "Missing required command: uv. Please install uv (https://github.com/astral-sh/uv)."
}

if (-not (Test-CommandExists "pnpm")) {
  Write-Error "Missing required command: pnpm. Please install pnpm (npm install -g pnpm)."
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Starting Murf + LiveKit Day 4 Voice Agent" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Sync backend dependencies
Write-Host "`n[1/3] Preparing Backend Python Environment..." -ForegroundColor Yellow
Set-Location "$repoRoot\backend"
uv sync

# 2. Install frontend dependencies
Write-Host "`n[2/3] Preparing Frontend Next.js Environment..." -ForegroundColor Yellow
Set-Location "$repoRoot\frontend"
pnpm install

# 3. Launch Backend and Frontend services
Write-Host "`n[3/3] Launching Backend & Frontend services in separate windows..." -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\backend'; Write-Host '--- Starting Backend Voice Agent ---' -ForegroundColor Green; uv run python src/agent.py dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\frontend'; Write-Host '--- Starting Frontend Web UI ---' -ForegroundColor Green; pnpm dev"

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host " Services launched successfully!" -ForegroundColor Green
Write-Host " Open your browser at: http://localhost:3000" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

