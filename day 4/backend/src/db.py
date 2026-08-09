import difflib
import json
import logging
import os
import sqlite3
import uuid

logger = logging.getLogger("agent")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "local_commerce.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            language_preference TEXT DEFAULT 'Hindi',
            facts TEXT,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def get_user(name: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, name, language_preference, facts, last_interaction FROM users")
    rows = c.fetchall()
    conn.close()

    if not rows:
        return None

    names = [row[1] for row in rows]
    matches = difflib.get_close_matches(name, names, n=1, cutoff=0.6)

    if matches:
        matched_name = matches[0]
        for row in rows:
            if row[1].lower() == matched_name.lower():
                try:
                    facts = json.loads(row[3]) if row[3] else {}
                except json.JSONDecodeError:
                    facts = {}
                return {
                    "user_id": row[0],
                    "name": row[1],
                    "language_preference": row[2],
                    "facts": facts,
                    "last_interaction": row[4],
                }

    return None


def save_user(name: str, facts: dict, language_preference: str = "Hindi"):
    existing = get_user(name)
    user_id = existing["user_id"] if existing else f"usr_{uuid.uuid4().hex[:8]}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    facts_json = json.dumps(facts)
    c.execute(
        """
        INSERT INTO users (user_id, name, language_preference, facts, last_interaction)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            language_preference=excluded.language_preference,
            facts=excluded.facts,
            last_interaction=CURRENT_TIMESTAMP
    """,
        (user_id, name, language_preference, facts_json),
    )
    conn.commit()
    conn.close()
    logger.info(f"User {name} ({user_id}) saved/updated in database.")
    return user_id
