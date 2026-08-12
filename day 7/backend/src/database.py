"""Database utilities for persisting user facts and profiles.

This module handles all database operations for Day 4:
- Initialize SQLite database
- Look up returning users
- Save/update user profiles and facts
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, Any

logger = logging.getLogger("agent.database")

# Database path (relative to backend root)
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def init_database():
    """Initialize SQLite database with schema if it doesn't exist."""
    db_path = DB_PATH.parent
    db_path.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).parent.parent / "data" / "schema.sql"

    try:
        with sqlite3.connect(DB_PATH) as conn:
            if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
                logger.info(f"Initializing database at {DB_PATH}")
                with open(schema_path, "r") as f:
                    conn.executescript(f.read())
                conn.commit()
                logger.info("Database initialized successfully")
            else:
                logger.info(f"Database already exists at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Look up a user's profile and facts by user_id.

    Args:
        user_id: The unique user identifier (from localStorage/room name)

    Returns:
        Dictionary with user data {name, language_preference, facts, last_interaction}
        or None if user not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, language_preference, facts, last_interaction FROM users WHERE user_id = ?",
                (user_id,),
            )
            row = cursor.fetchone()

            if row:
                facts_str = row[2]
                facts = json.loads(facts_str) if facts_str else {}
                return {
                    "name": row[0],
                    "language_preference": row[1],
                    "facts": facts,
                    "last_interaction": row[3],
                }
            return None
    except Exception as e:
        logger.error(f"Error looking up user {user_id}: {e}")
        return None


def save_user(
    user_id: str, name: str, facts: Dict[str, Any], language_preference: str = "en"
) -> bool:
    """Save or update a user's profile and facts.

    Args:
        user_id: The unique user identifier
        name: Customer's name
        facts: Dictionary of facts to remember (e.g., {past_orders, usual_quantity, preferred_slot})
        language_preference: Language preference (default: 'en')

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            facts_json = json.dumps(facts)

            # Check if user exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone() is not None

            if exists:
                # Update existing user
                cursor.execute(
                    """UPDATE users 
                       SET name = ?, facts = ?, language_preference = ?, last_interaction = ?
                       WHERE user_id = ?""",
                    (name, facts_json, language_preference, now, user_id),
                )
                logger.info(f"Updated user profile: {user_id}")
            else:
                # Insert new user
                cursor.execute(
                    """INSERT INTO users (user_id, name, language_preference, facts, created_at, last_interaction)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, name, language_preference, facts_json, now, now),
                )
                logger.info(f"Created new user profile: {user_id}")

            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error saving user {user_id}: {e}")
        return False


def update_last_interaction(user_id: str) -> bool:
    """Update the last_interaction timestamp for a user.

    Args:
        user_id: The unique user identifier

    Returns:
        True if updated successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()

            cursor.execute(
                "UPDATE users SET last_interaction = ? WHERE user_id = ?",
                (now, user_id),
            )
            conn.commit()
            logger.info(f"Updated last_interaction for user: {user_id}")
            return True
    except Exception as e:
        logger.error(f"Error updating last_interaction for {user_id}: {e}")
        return False


def delete_user(user_id: str) -> bool:
    """Delete a user's profile (for "forget me" feature).

    Args:
        user_id: The unique user identifier

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.info(f"Deleted user profile: {user_id}")
            return True
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return False
