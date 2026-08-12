"""
database_calls.py
──────────────────
SQLite database layer for Day 8 Voice Agent Performance Dashboard.
Records call outcomes for browser and SIP calls.
Calculates deterministic dashboard statistics (Total, Successful, Failed).
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "calls.db"


def _get_conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_calls_db() -> None:
    """Initialize the calls table."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT UNIQUE NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'browser', -- 'browser' or 'sip'
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration INTEGER DEFAULT 0,
                outcome TEXT NOT NULL DEFAULT 'failed', -- 'successful' or 'failed'
                reason TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()


def mask_identifier(ident: str) -> str:
    """Anonymize/mask caller IDs or phone numbers for privacy compliance."""
    if not ident:
        return "Anonymous"
    # If it's a phone number (e.g. +919876543210)
    if ident.startswith("+") or ident.isdigit():
        if len(ident) > 4:
            return "*" * (len(ident) - 4) + ident[-4:]
        return "*****"
    # If it's a long room/participant ID
    if len(ident) > 12:
        return ident[:4] + "..." + ident[-4:]
    return ident


def record_call_start(call_id: str, call_type: str = "browser") -> bool:
    """Record when a call begins."""
    init_calls_db()
    started_at = datetime.utcnow().isoformat()
    try:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO calls (call_id, call_type, started_at, outcome, reason)
                VALUES (?, ?, ?, 'failed', 'Call in progress')
                """,
                (call_id, call_type, started_at),
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[calls_db] Error recording call start: {e}")
        return False


def record_call_end(
    call_id: str,
    outcome: str,
    reason: str = "",
    duration: Optional[int] = None,
    ended_at: Optional[str] = None,
) -> bool:
    """Record call end and save outcome (successful/failed)."""
    init_calls_db()
    if not ended_at:
        ended_at = datetime.utcnow().isoformat()

    valid_outcomes = {"successful", "failed"}
    if outcome not in valid_outcomes:
        outcome = "failed"

    try:
        with _get_conn() as conn:
            # Get start time if duration not passed
            row = conn.execute(
                "SELECT started_at FROM calls WHERE call_id = ?", (call_id,)
            ).fetchone()

            calc_duration = duration if duration is not None else 0
            if row and row["started_at"] and calc_duration == 0:
                try:
                    start_dt = datetime.fromisoformat(row["started_at"])
                    end_dt = datetime.fromisoformat(ended_at)
                    calc_duration = int((end_dt - start_dt).total_seconds())
                except Exception:
                    calc_duration = 0

            conn.execute(
                """
                UPDATE calls
                SET ended_at = ?,
                    duration = ?,
                    outcome = ?,
                    reason = ?
                WHERE call_id = ?
                """,
                (ended_at, calc_duration, outcome, reason, call_id),
            )
            
            # If call record didn't exist before, insert it directly
            if conn.total_changes == 0:
                conn.execute(
                    """
                    INSERT INTO calls (call_id, call_type, started_at, ended_at, duration, outcome, reason)
                    VALUES (?, 'browser', ?, ?, ?, ?, ?)
                    """,
                    (call_id, ended_at, ended_at, calc_duration, outcome, reason),
                )

            conn.commit()
        return True
    except Exception as e:
        print(f"[calls_db] Error recording call end: {e}")
        return False


def get_dashboard_stats() -> Dict[str, int]:
    """Return dashboard summary numbers directly from SQLite database."""
    init_calls_db()
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
        successful = conn.execute(
            "SELECT COUNT(*) FROM calls WHERE outcome = 'successful'"
        ).fetchone()[0]
        failed = conn.execute(
            "SELECT COUNT(*) FROM calls WHERE outcome = 'failed'"
        ).fetchone()[0]

    return {
        "totalCalls": total,
        "successfulCalls": successful,
        "failedCalls": failed,
    }


def get_recent_calls(limit: int = 50) -> List[Dict[str, Any]]:
    """Return list of recent call records for dashboard table."""
    init_calls_db()
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, call_id, call_type, started_at, ended_at, duration, outcome, reason, created_at
            FROM calls
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    calls = []
    for r in rows:
        c = dict(r)
        c["masked_call_id"] = mask_identifier(c["call_id"])
        calls.append(c)
    return calls
