"""
database_escalations.py
───────────────────────
Escalation management for Ratan Kirana & General Store (Day 7).

Handles:
- Creating human-help escalation requests
- Looking up escalations by ID or user
- Checking for duplicates (same user + reason already open)
- Updating escalation status

Database: data/escalations.db (SQLite)
"""

import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("database_escalations")

# DB path — data/escalations.db relative to backend/
_DB_PATH = Path(__file__).parent.parent / "data" / "escalations.db"

# Schema path for initialization
_SCHEMA_PATH = Path(__file__).parent.parent / "data" / "schema_escalations.sql"


def _get_conn() -> sqlite3.Connection:
    """Get a connection to the escalations database."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_escalations_db() -> None:
    """Initialize the escalations database with schema if it doesn't exist."""
    try:
        with _get_conn() as conn:
            # Check if table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='escalations'"
            )
            if cursor.fetchone() is None:
                logger.info("Initializing escalations database…")
                if _SCHEMA_PATH.exists():
                    with open(_SCHEMA_PATH) as f:
                        conn.executescript(f.read())
                    logger.info("Escalations database initialized successfully")
                else:
                    logger.error(f"Schema file not found: {_SCHEMA_PATH}")
            else:
                logger.info("Escalations database already exists")
    except Exception as e:
        logger.error(f"Failed to initialize escalations database: {e}")
        raise


def _generate_escalation_id() -> str:
    """Generate a unique escalation ID like ESC-20260812-001."""
    today = date.today().isoformat().replace("-", "")
    try:
        with _get_conn() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM escalations WHERE escalation_id LIKE ?",
                (f"ESC-{today}-%",),
            ).fetchone()[0]
            seq = count + 1
    except Exception:
        seq = 1
    return f"ESC-{today}-{seq:03d}"


def get_escalation_by_user_and_reason(
    user_id: str, reason: str
) -> Optional[dict[str, Any]]:
    """Check if there's already an open escalation for this user + reason.

    Used to prevent duplicate escalations.

    Args:
        user_id: The customer's user_id
        reason: The escalation reason (payment_dispute, refund_request, order_dispute)

    Returns:
        The existing open escalation dict, or None if no duplicate exists
    """
    try:
        with _get_conn() as conn:
            row = conn.execute(
                """SELECT * FROM escalations
                   WHERE user_id = ? AND reason = ? AND status = 'open'
                   ORDER BY created_at DESC LIMIT 1""",
                (user_id, reason),
            ).fetchone()

            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error checking for duplicate escalation: {e}")
        return None


def create_escalation(
    user_id: str,
    customer_name: str,
    reason: str,
    summary: str,
    what_agent_checked: str = "",
    urgency: str = "medium",
    language: str = "en",
    preferred_followup: str = "call",
) -> Optional[str]:
    """Create a new escalation request in the database.

    Args:
        user_id: The customer's user_id
        customer_name: Customer's name
        reason: payment_dispute, refund_request, or order_dispute
        summary: Short summary of the issue (should be PII-stripped)
        what_agent_checked: What the agent already verified
        urgency: low, medium, high, or emergency
        language: Customer's language (en, hi, gu)
        preferred_followup: How they want to be contacted (call, whatsapp, email)

    Returns:
        The escalation_id if created successfully, None on failure
    """
    escalation_id = _generate_escalation_id()
    now = datetime.utcnow().isoformat()

    try:
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO escalations
                   (escalation_id, user_id, customer_name, reason, urgency,
                    summary, what_agent_checked, language, preferred_followup,
                    status, email_sent, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    escalation_id,
                    user_id,
                    customer_name,
                    reason,
                    urgency,
                    summary,
                    what_agent_checked,
                    language,
                    preferred_followup,
                    "open",
                    0,
                    now,
                    now,
                ),
            )
            logger.info(f"Escalation created: {escalation_id} for {customer_name}")
            return escalation_id

    except Exception as e:
        logger.error(f"Failed to create escalation: {e}")
        return None


def mark_email_sent(escalation_id: str) -> bool:
    """Mark that the email notification was sent for an escalation."""
    try:
        with _get_conn() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """UPDATE escalations
                   SET email_sent = 1, updated_at = ?
                   WHERE escalation_id = ?""",
                (now, escalation_id),
            )
            return True
    except Exception as e:
        logger.error(f"Failed to mark email sent for {escalation_id}: {e}")
        return False


def get_escalation_by_id(escalation_id: str) -> Optional[dict[str, Any]]:
    """Look up an escalation by its ID.

    Args:
        escalation_id: The escalation ID (e.g., ESC-20260812-001)

    Returns:
        Escalation dict, or None if not found
    """
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM escalations WHERE escalation_id = ?",
                (escalation_id,),
            ).fetchone()

            if row is None:
                return None
            return dict(row)
    except Exception as e:
        logger.error(f"Error looking up escalation {escalation_id}: {e}")
        return None


def get_open_escalations() -> list[dict[str, Any]]:
    """Get all open escalation requests, ordered by urgency and creation time.

    Returns:
        List of open escalation dicts
    """
    urgency_order = {"emergency": 0, "high": 1, "medium": 2, "low": 3}
    try:
        with _get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM escalations
                   WHERE status = 'open'
                   ORDER BY created_at DESC"""
            ).fetchall()

            escalations = [dict(row) for row in rows]
            # Sort by urgency priority
            escalations.sort(key=lambda e: urgency_order.get(e["urgency"], 2))
            return escalations
    except Exception as e:
        logger.error(f"Error getting open escalations: {e}")
        return []


def update_escalation_status(
    escalation_id: str, status: str, notes: Optional[str] = None
) -> bool:
    """Update the status of an escalation.

    Args:
        escalation_id: The escalation ID
        status: New status (open, in_progress, resolved)
        notes: Optional resolution notes

    Returns:
        True if updated successfully
    """
    try:
        with _get_conn() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """UPDATE escalations
                   SET status = ?, updated_at = ?
                   WHERE escalation_id = ?""",
                (status, now, escalation_id),
            )
            logger.info(f"Escalation {escalation_id} status updated to {status}")
            return True
    except Exception as e:
        logger.error(f"Failed to update escalation {escalation_id}: {e}")
        return False
