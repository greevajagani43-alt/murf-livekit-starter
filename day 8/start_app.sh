#!/usr/bin/env bash
# macOS/Linux launcher script for Day 8
echo "================================================================="
echo " Starting Day 8 — Voice Agent Performance Dashboard"
echo " Track: Local Commerce | Murf Falcon TTS | Real SQLite Metrics"
echo "================================================================="

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Start Dashboard REST API
(cd "$DIR/backend" && uv run python src/dashboard_server.py) &

# Start Voice Agent
(cd "$DIR/backend" && uv sync && uv run python src/agent.py dev) &

# Start Frontend UI
(cd "$DIR/frontend" && pnpm install && pnpm dev) &

echo "Services started. Dashboard available at http://localhost:3000"
wait
