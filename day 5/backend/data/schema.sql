-- SQLite schema for user persistence (Day 4)
-- Table: users — stores customer profiles and facts

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    language_preference TEXT DEFAULT 'en',
    facts TEXT NOT NULL,  -- JSON string: {past_orders, usual_quantity, preferred_slot}
    last_interaction TEXT,  -- ISO timestamp
    created_at TEXT NOT NULL  -- ISO timestamp
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
