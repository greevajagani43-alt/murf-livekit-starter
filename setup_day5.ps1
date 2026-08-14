$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$day5Dir   = Join-Path $scriptDir "day 5"
$repoUrl   = "https://github.com/KavanBhavsar35/voice-for-bharat-challenge-2026.git"

# Fill in your API keys below (copy from your .env.local files)
$LIVEKIT_URL        = "YOUR_LIVEKIT_URL"
$LIVEKIT_API_KEY    = "YOUR_LIVEKIT_API_KEY"
$LIVEKIT_API_SECRET = "YOUR_LIVEKIT_API_SECRET"
$MURF_API_KEY       = "YOUR_MURF_API_KEY"
$DEEPGRAM_API_KEY   = "YOUR_DEEPGRAM_API_KEY"
$GOOGLE_API_KEY     = "YOUR_GOOGLE_API_KEY"
$AGENT_NAME         = "my-agent"

Write-Host ""
Write-Host "=== Step 1: Cloning repo into 'day 5' ===" -ForegroundColor Cyan

if (Test-Path $day5Dir) {
    Write-Host "'day 5' already exists - pulling latest..." -ForegroundColor Yellow
    Push-Location $day5Dir
    git pull
    Pop-Location
} else {
    git clone $repoUrl $day5Dir
}

Write-Host ""
Write-Host "=== Step 2: Writing backend .env.local ===" -ForegroundColor Cyan

$backendEnvPath = Join-Path $day5Dir "backend\.env.local"
$backendLines = @(
    "LIVEKIT_URL=$LIVEKIT_URL",
    "LIVEKIT_API_KEY=$LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET",
    "MURF_API_KEY=$MURF_API_KEY",
    "DEEPGRAM_API_KEY=$DEEPGRAM_API_KEY",
    "GOOGLE_API_KEY=$GOOGLE_API_KEY"
)
$backendLines | Set-Content -Path $backendEnvPath -Encoding UTF8
Write-Host "Written: $backendEnvPath" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 3: Writing frontend .env.local ===" -ForegroundColor Cyan

$frontendEnvPath = Join-Path $day5Dir "frontend\.env.local"
$frontendLines = @(
    "LIVEKIT_URL=$LIVEKIT_URL",
    "LIVEKIT_API_KEY=$LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET",
    "AGENT_NAME=$AGENT_NAME"
)
$frontendLines | Set-Content -Path $frontendEnvPath -Encoding UTF8
Write-Host "Written: $frontendEnvPath" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 4: Installing backend deps (uv sync) ===" -ForegroundColor Cyan

Push-Location (Join-Path $day5Dir "backend")
uv sync
Pop-Location
Write-Host "Backend deps installed." -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 5: Downloading agent model files ===" -ForegroundColor Cyan

Push-Location (Join-Path $day5Dir "backend")
uv run python src/agent.py download-files
Pop-Location

Write-Host ""
Write-Host "=== Step 6: Installing frontend deps (pnpm install) ===" -ForegroundColor Cyan

Push-Location (Join-Path $day5Dir "frontend")
pnpm install
Pop-Location
Write-Host "Frontend deps installed." -ForegroundColor Green

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Day 5 setup complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the app:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option A - bundled launcher:" -ForegroundColor White
Write-Host "    cd '$day5Dir'" -ForegroundColor Gray
Write-Host "    .\start_app.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  Option B - two terminals:" -ForegroundColor White
Write-Host "    Terminal 1 (backend):" -ForegroundColor Gray
Write-Host "      cd '$day5Dir\backend'" -ForegroundColor Gray
Write-Host "      uv run python src/agent.py dev" -ForegroundColor Gray
Write-Host ""
Write-Host "    Terminal 2 (frontend):" -ForegroundColor Gray
Write-Host "      cd '$day5Dir\frontend'" -ForegroundColor Gray
Write-Host "      pnpm dev" -ForegroundColor Gray
Write-Host ""
