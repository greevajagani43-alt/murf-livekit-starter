-- Escalations table for Ratan Kirana Store (Day 7)
-- Stores human-help requests created by the voice agent

CREATE TABLE IF NOT EXISTS escalations (
    escalation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    reason TEXT NOT NULL,  -- payment_dispute, refund_request, order_dispute
    urgency TEXT DEFAULT 'medium',  -- low, medium, high, emergency
    summary TEXT NOT NULL,  -- Short summary for the human reviewer
    what_agent_checked TEXT,  -- What the agent already verified
    language TEXT DEFAULT 'en',  -- Customer's language (en, hi, gu)
    preferred_followup TEXT DEFAULT 'call',  -- call, whatsapp, email
    status TEXT DEFAULT 'open',  -- open, in_progress, resolved
    email_sent INTEGER DEFAULT 0,  -- 0=not sent, 1=sent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_escalations_user_id ON escalations(user_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);
CREATE INDEX IF NOT EXISTS idx_escalations_reason ON escalations(reason);
