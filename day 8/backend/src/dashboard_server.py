"""
dashboard_server.py
───────────────────
FastAPI HTTP REST API server for Day 8 Voice Agent Performance Dashboard.
Exposes live database call metrics to the Next.js frontend UI.

Endpoints:
    GET  /api/dashboard/stats  → Total, Successful, and Failed counts
    GET  /api/calls            → Recent call log history (masked for privacy)
    POST /api/calls/record     → Record a call outcome manually (REST fallback)
    DELETE /api/calls/reset    → Clear calls for clean test verification
    GET  /health               → Health check probe
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))

from database_calls import (
    get_dashboard_stats,
    get_recent_calls,
    init_calls_db,
    record_call_end,
    record_call_start,
    _get_conn,
)

load_dotenv(Path(__file__).parent.parent / ".env.local")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_calls_db()
    yield


app = FastAPI(title="Voice Agent Performance Dashboard API", lifespan=lifespan)

# Allow Next.js frontend origin (port 3000, 3001, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class CallRecordPayload(BaseModel):
    call_id: str
    call_type: str = "browser"
    outcome: str = "failed"
    reason: Optional[str] = None
    duration: Optional[int] = 0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard/stats")
def get_stats():
    """Return Total, Successful, and Failed call metrics from real database data."""
    try:
        stats = get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls")
def get_calls(limit: int = Query(50, ge=1, le=200)):
    """Return recent calls list with anonymized call IDs for privacy protection."""
    try:
        calls = get_recent_calls(limit=limit)
        return calls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calls/record")
def record_call(payload: CallRecordPayload):
    """Record a completed call outcome via REST API."""
    try:
        record_call_start(call_id=payload.call_id, call_type=payload.call_type)
        ok = record_call_end(
            call_id=payload.call_id,
            outcome=payload.outcome,
            reason=payload.reason or "",
            duration=payload.duration or 0,
        )
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to record call")
        return {"success": True, "call_id": payload.call_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/calls/reset")
def reset_calls():
    """Reset call database records for clean state testing."""
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM calls")
            conn.commit()
        return {"success": True, "message": "Call database reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
