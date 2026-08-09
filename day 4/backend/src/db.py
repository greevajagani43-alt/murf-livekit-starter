import json
import logging
import os
import sqlite3
import difflib

logger = logging.getLogger("agent")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "local_commerce.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY COLLATE NOCASE,
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
    c.execute("SELECT name, facts FROM users")
    rows = c.fetchall()
    conn.close()

    if not rows:
        return None

    names = [row[0] for row in rows]
    # Find the closest matching name (helps with speech-to-text typos like Jatim vs Jatin)
    matches = difflib.get_close_matches(name, names, n=1, cutoff=0.6)
    
    if matches:
        matched_name = matches[0]
        for row in rows:
            if row[0] == matched_name:
                try:
                    facts = json.loads(row[1]) if row[1] else {}
                except json.JSONDecodeError:
                    facts = {}
                return {"name": matched_name, "facts": facts}
                
    return None


def save_user(name: str, facts: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    facts_json = json.dumps(facts)
    c.execute(
        """
        INSERT INTO users (name, facts, last_interaction)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(name) DO UPDATE SET
            facts=excluded.facts,
            last_interaction=CURRENT_TIMESTAMP
    """,
        (name, facts_json),
    )
    conn.commit()
    conn.close()
    logger.info(f"User {name} saved/updated in database.")
