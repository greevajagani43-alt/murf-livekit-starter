-- Calls tracking table for Ratan Kirana Store (Day 8)
-- Records call outcomes for the analytics dashboard
--
-- Success definition (Local Commerce track):
--   A successful call = the customer completes an order (place_order succeeds)
--   A failed call = the session ends without a completed order

CREATE TABLE IF NOT EXISTS calls (
    call_id TEXT PRIMARY KEY,
    user_id TEXT,
    channel TEXT DEFAULT 'browser',         -- browser or sip
    outcome TEXT NOT NULL,                  -- success or failed
    failure_reason TEXT,                    -- user_hangup, no_order, incomplete, tool_error
    duration_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calls_outcome ON calls(outcome);
CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at);
