$ErrorActionPreference = "Stop"

function Test-CommandExists {
  param([string]$CommandName)
<<<<<<< HEAD

=======
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
  return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandExists "uv")) {
<<<<<<< HEAD
  Write-Error "Missing required command: uv"
}

if (-not (Test-CommandExists "pnpm")) {
  Write-Error "Missing required command: pnpm"
=======
  Write-Error "Missing required command: uv. Please install uv (https://github.com/astral-sh/uv)."
}

if (-not (Test-CommandExists "pnpm")) {
  Write-Error "Missing required command: pnpm. Please install pnpm (npm install -g pnpm)."
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

<<<<<<< HEAD
# Start each service in its own PowerShell window so logs remain visible.
if (Test-CommandExists "livekit-server") {
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot'; livekit-server --dev"
} else {
  Write-Warning "livekit-server was not found. Skipping local LiveKit startup and using your configured LIVEKIT_URL instead."
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\backend'; uv run python src/agent.py dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\frontend'; pnpm dev"

Write-Host "Started backend and frontend in separate PowerShell windows."
=======
# Clear any stale process occupying port 3000
$stalePids = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($stalePids) {
  foreach ($p in $stalePids) {
    if ($p -gt 4) {
      Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
  }
}
# Ensure frontend .env.local exists from .env.example if missing
if ((-not (Test-Path "$repoRoot\frontend\.env.local")) -and (Test-Path "$repoRoot\frontend\.env.example")) {
  Copy-Item "$repoRoot\frontend\.env.example" "$repoRoot\frontend\.env.local"
  Add-Content "$repoRoot\frontend\.env.local" "`nAGENT_NAME=my-agent"
}

# Ensure backend .env.local exists from .env.example if missing
if ((-not (Test-Path "$repoRoot\backend\.env.local")) -and (Test-Path "$repoRoot\backend\.env.example")) {
  Copy-Item "$repoRoot\backend\.env.example" "$repoRoot\backend\.env.local"
}

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

>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
