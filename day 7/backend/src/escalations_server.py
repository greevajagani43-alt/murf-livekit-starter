"""
escalations_server.py
─────────────────────
FastAPI HTTP server exposing escalation requests over HTTP
so the Next.js frontend dashboard can display them.

Endpoints:
    GET  /escalations          → all escalations (sorted by urgency)
    GET  /escalations/{id}     → single escalation
    PATCH /escalations/{id}    → update status
    GET  /health               → liveness probe
"""

import sys
import os
from pathlib import Path

# Ensure we can import siblings (database_escalations, etc.)
sys.path.insert(0, str(Path(__file__).parent))

from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env.local")

from database_escalations import (
    get_open_escalations,
    get_escalation_by_id,
    init_escalations_db,
    update_escalation_status,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_escalations_db()
    yield


app = FastAPI(title="Saathi Escalations API", lifespan=lifespan)

# Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


class StatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/escalations")
def list_escalations(status: Optional[str] = Query(None)):
    """List escalations. Optionally filter by status (open, in_progress, resolved)."""
    from database_escalations import _get_conn

    try:
        with _get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM escalations WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM escalations ORDER BY created_at DESC"
                ).fetchall()

        urgency_order = {"emergency": 0, "high": 1, "medium": 2, "low": 3}
        escalations = [dict(row) for row in rows]
        escalations.sort(key=lambda e: urgency_order.get(e["urgency"], 2))
        return escalations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/escalations/{escalation_id}")
def get_escalation(escalation_id: str):
    """Get a single escalation by ID."""
    esc = get_escalation_by_id(escalation_id)
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return esc


@app.patch("/escalations/{escalation_id}")
def update_status(escalation_id: str, body: StatusUpdate):
    """Update an escalation's status."""
    valid = {"open", "in_progress", "resolved"}
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")

    ok = update_escalation_status(escalation_id, body.status, body.notes)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update status")
    return {"success": True, "escalation_id": escalation_id, "status": body.status}
