# Day 8 — Voice Agent Performance Dashboard (Local Commerce Track)

Welcome to **Day 8** of the **Murf AI 10 Days of Voice Agents (#VoiceForBharat 2026)** challenge!

This project implements a complete, real-time **Voice Agent Performance Dashboard** built from scratch. It records real browser and SIP call outcomes into a SQLite database and computes live performance metrics without fake or hardcoded data.

---

## 🏗️ Architecture

```
                               ┌───────────────────────────┐
                               │  Browser / SIP Voice Call │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  LiveKit Voice Agent      │
                               │  (Murf Falcon + Gemini)   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼ (on_session_end)
                               ┌───────────────────────────┐
                               │  SQLite Database          │
                               │  (data/calls.db)          │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
┌──────────────────────────┐    ┌───────────────────────────┐
│ Next.js Dashboard UI     │ ◄──┤ FastAPI REST Server       │
│ (http://localhost:3000)  │    │ (http://localhost:8003)   │
└──────────────────────────┘    └───────────────────────────┘
```

---

## 🛠️ Technologies Used

- **TTS**: Murf Falcon (`livekit-murf`)
- **STT**: Deepgram Nova-3 (`deepgram`)
- **LLM**: Google Gemini (`google`)
- **Backend API**: FastAPI (`fastapi`, `uvicorn`)
- **Database**: SQLite (`sqlite3`)
- **Frontend UI**: Next.js (TypeScript, React, Tailwind CSS)
- **Real-Time Transport**: LiveKit Agents SDK (`livekit-agents ~1.4`)

---

## 🔐 Environment Variables

Create `.env.local` inside `backend/` and `frontend/` using `.env.example`:

| Variable Name | Purpose | Exposed in Frontend? |
|---------------|---------|-----------------------|
| `LIVEKIT_URL` | LiveKit WebSocket endpoint | Yes (via Token API) |
| `LIVEKIT_API_KEY` | LiveKit API Key | No |
| `LIVEKIT_API_SECRET` | LiveKit API Secret | No |
| `LIVEKIT_SIP_OUTBOUND_TRUNK_ID` | SIP Outbound Trunk ID (`ST_Jq6TWCA78sef`) | No |
| `MURF_API_KEY` | Murf Falcon TTS API Key | No |
| `DEEPGRAM_API_KEY` | Deepgram STT API Key | No |
| `GOOGLE_API_KEY` | Gemini LLM API Key | No |

---

## 📊 Database Schema (`data/calls.db`)

The call outcomes table is created automatically:

```sql
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT UNIQUE NOT NULL,
    call_type TEXT NOT NULL DEFAULT 'browser', -- 'browser' or 'sip'
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration INTEGER DEFAULT 0,               -- in seconds
    outcome TEXT NOT NULL DEFAULT 'failed',    -- 'successful' or 'failed'
    reason TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 🎯 How Call Outcomes are Determined (Local Commerce Track)

- **SUCCESSFUL**: The caller finds a product or completes a product enquiry (e.g. asking *"Do you have wireless headphones?"* or checking prices/stock of Atta, Milk, Oil, Rice).
- **FAILED**: The call disconnects before completing a product enquiry.

The agent tracks enquiry status using `mark_enquiry_completed()`. When the session ends, `record_call_end()` writes the deterministic result to SQLite.

---

## 🚀 How to Run

### Option 1: PowerShell Script (Windows)
```powershell
.\start_app.ps1
```

### Option 2: Manual Commands

#### 1. Start Backend Agent:
```bash
cd backend
uv sync
uv run python src/agent.py dev
```

#### 2. Start Dashboard REST Server:
```bash
cd backend
uv run python src/dashboard_server.py
```

#### 3. Start Frontend Dashboard UI:
```bash
cd frontend
pnpm install
pnpm dev
```

Dashboard UI will be available at **`http://localhost:3000`**.

---

## 🧪 How to Test

### Test 1 — Empty Database State
Click **"Reset Test DB"** on the dashboard.
- **Expected**: Total Calls = 0, Successful Calls = 0, Failed Calls = 0.

### Test 2 — Successful Call
1. Click **"Baat Karo Saathi Se"** on the dashboard.
2. Ask: *"Do you have wireless headphones?"* or *"What is the price of Atta?"*
3. Saathi answers with price and stock details.
4. Click **"End Call"**.
- **Expected**: Total Calls = 1, Successful Calls = 1, Failed Calls = 0.

### Test 3 — Failed Call
1. Click **"Baat Karo Saathi Se"**.
2. Immediately click **"End Call"** without asking any product question.
- **Expected**: Total Calls = 2, Successful Calls = 1, Failed Calls = 1.

---

## 🔒 Security & Privacy

1. All call IDs are anonymized and masked (`call_1771...` or `*****1234`).
2. No full transcripts, passwords, PINs, or OTPs are saved to the database.
3. Secret API keys are kept strictly inside `.env.local` and never exposed to git.
