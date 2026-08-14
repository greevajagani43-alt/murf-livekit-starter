"""
database_calls.py
─────────────────
Call analytics tracking for Ratan Kirana Store (Day 8).

Tracks the outcome of every voice call:
  - success: customer completed an order (place_order succeeded)
  - failed: session ended without a completed order

Success definition (Local Commerce track):
  A successful call = the caller completes a product enquiry or places an order.
  Specifically, place_order returning a successful order ID = success.
  Everything else (hangup, no order, incomplete) = failed.

Database: data/calls.db (SQLite)
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("database_calls")

# DB path — data/calls.db relative to backend/
_DB_PATH = Path(__file__).parent.parent / "data" / "calls.db"
_SCHEMA_PATH = Path(__file__).parent.parent / "data" / "schema_calls.sql"


def _get_conn() -> sqlite3.Connection:
    """Get a connection to the calls database."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_calls_db() -> None:
    """Initialize the calls database with schema if it doesn't exist."""
    try:
        with _get_conn() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='calls'"
            )
            if cursor.fetchone() is None:
                logger.info("Initializing calls database…")
                if _SCHEMA_PATH.exists():
                    with open(_SCHEMA_PATH) as f:
                        conn.executescript(f.read())
                    logger.info("Calls database initialized successfully")
                else:
                    logger.error("Schema file not found: %s", _SCHEMA_PATH)
            else:
                logger.info("Calls database already exists")
    except Exception as e:
        logger.error("Failed to initialize calls database: %s", e)
        raise


def record_call(
    call_id: str,
    user_id: str,
    outcome: str,
    channel: str = "browser",
    failure_reason: Optional[str] = None,
    duration_seconds: int = 0,
) -> bool:
    """Record a call outcome to the database.

    Args:
        call_id: Unique call/session identifier
        user_id: The customer's user_id
        outcome: 'success' or 'failed'
        channel: 'browser' or 'sip'
        failure_reason: If failed, why (user_hangup, no_order, incomplete, etc.)
        duration_seconds: Call duration in seconds

    Returns:
        True if saved successfully
    """
    try:
        with _get_conn() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """INSERT OR REPLACE INTO calls
                   (call_id, user_id, channel, outcome,
                    failure_reason, duration_seconds, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    call_id,
                    user_id,
                    channel,
                    outcome,
                    failure_reason,
                    duration_seconds,
                    now,
                ),
            )
            logger.info(
                "Recorded call %s: outcome=%s, channel=%s",
                call_id,
                outcome,
                channel,
            )
            return True
    except Exception as e:
        logger.error("Failed to record call %s: %s", call_id, e)
        return False


def get_call_stats() -> dict[str, int]:
    """Get aggregated call statistics.

    Returns:
        Dict with keys: total, successful, failed
    """
    try:
        with _get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
            successful = conn.execute(
                "SELECT COUNT(*) FROM calls WHERE outcome = 'success'"
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM calls WHERE outcome = 'failed'"
            ).fetchone()[0]

            return {
                "total": total,
                "successful": successful,
                "failed": failed,
            }
    except Exception as e:
        logger.error("Failed to get call stats: %s", e)
        return {"total": 0, "successful": 0, "failed": 0}


def get_recent_calls(limit: int = 20) -> list[dict[str, Any]]:
    """Get recent call records for the dashboard history table.

    Privacy: Does NOT return customer names, phone numbers,
    addresses, or conversation content.

    Args:
        limit: Max number of records to return

    Returns:
        List of call dicts (call_id, user_id, channel, outcome,
        failure_reason, duration_seconds, created_at)
    """
    try:
        with _get_conn() as conn:
            rows = conn.execute(
                """SELECT call_id, user_id, channel, outcome,
                          failure_reason, duration_seconds, created_at
                   FROM calls
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()

            calls = []
            for row in rows:
                calls.append(
                    {
                        "call_id": row["call_id"],
                        "channel": row["channel"],
                        "outcome": row["outcome"],
                        "failure_reason": row["failure_reason"],
                        "duration_seconds": row["duration_seconds"],
                        "created_at": row["created_at"],
                    }
                )
            return calls
    except Exception as e:
        logger.error("Failed to get recent calls: %s", e)
        return []
