# Day 6 — Outbound Calls with Twilio + LiveKit

> **Track: Local Commerce**
> Saathi (the voice agent for Ratan Kirana Store) now *calls customers proactively*
> to remind them when their usual groceries need restocking.

---

## What's New in Day 6

| Day | Capability |
|-----|-----------|
| 1–3 | Basic browser-based voice agent |
| 4   | User memory with SQLite |
| 5   | Product catalogue, stock validation |
| **6** | **Outbound PSTN calls via Twilio SIP + LiveKit** |

---

## Architecture

```
trigger_call.py (CLI)
        │
        ▼
LiveKit SIP API  ──────────►  Twilio SIP Trunk  ──────────►  Customer's Phone
        │                                                          │
        ▼                                                          │
agent.py (voice pipeline)  ◄──────────────────────────────────────┘
  Deepgram STT → Gemini LLM → Murf Falcon TTS
```

---

## Quick Start

### Step 1 — Set up environment

```powershell
cd "day 6\backend"
copy .env.example .env.local
# Edit .env.local and fill in all values (see below)
```

### Step 2 — Install dependencies

```powershell
cd "day 6\backend"
uv sync
uv run python src/agent.py download-files   # first time only
```

### Step 3 — Set up Twilio SIP Trunk (one-time)

> See **Twilio Setup** section below for full instructions.

### Step 4 — Run the agent

```powershell
cd "day 6\backend"
uv run python src/agent.py dev
```

### Step 5 — Trigger an outbound call

```powershell
# From day 6\backend\
uv run python src/trigger_call.py --number +91XXXXXXXXXX --name "Your Name"

# Dry run (no actual call)
uv run python src/trigger_call.py --number +91XXXXXXXXXX --dry-run
```

### Step 6 — Or use the HTTP API

```powershell
# Start the trigger server
uv run uvicorn src.trigger_server:app --host 0.0.0.0 --port 8001 --reload

# In another terminal, call the API
curl -X POST http://localhost:8001/call `
  -H "Content-Type: application/json" `
  -d '{"phone_number": "+91XXXXXXXXXX", "customer_name": "Rahul", "reason": "restock"}'

# View API docs
# Open: http://localhost:8001/docs
```

---

## Twilio Setup (Step by Step)

### A. Get Twilio credentials

1. Sign up / log in at [console.twilio.com](https://console.twilio.com)
2. Note your **Account SID** and **Auth Token** from the dashboard
3. Get a Twilio phone number with voice capability

### B. Create a Twilio SIP Domain

1. Go to **Elastic SIP Trunking → SIP Domains → Create**
2. Set a domain name, e.g. `saathi.pstn.twilio.com`
3. Under **Voice**, set the **Request URL** to point to your LiveKit SIP endpoint
4. Save

### C. Create a LiveKit Outbound SIP Trunk

1. Go to [cloud.livekit.io](https://cloud.livekit.io) → **SIP → Trunks → Create Trunk**
2. Choose **Outbound**
3. Set the SIP server to your Twilio SIP domain
4. Add authentication (Twilio credentials)
5. Copy the **Trunk ID** (starts with `ST_`)
6. Paste it into `backend/.env.local` as `LIVEKIT_SIP_TRUNK_ID`

### D. Configure Twilio to accept LiveKit calls

In Twilio console:
- Set your SIP domain to send calls to LiveKit's SIP endpoint

---

## Outbound Call Script (First 2 Sentences)

Per Day 6 requirements, the first thing Saathi says on every outbound call:

> **"नमस्ते! मैं साथी हूँ, रतन किराना स्टोर की तरफ़ से बोल रहा हूँ।**
> **आपका आटा फिर से मँगाने का वक़्त आ गया है — अगर बात नहीं करनी तो बस कह दीजिए 'नहीं चाहिए' और मैं कॉल बंद कर दूँगा।"**

This satisfies the 3 requirements:
- ✅ **Who's calling**: "मैं साथी हूँ, रतन किराना स्टोर की तरफ़ से"
- ✅ **Why**: "आपका आटा फिर से मँगाने का वक़्त आ गया है"
- ✅ **How to stop**: "बस कह दीजिए 'नहीं चाहिए'"

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | ✅ | `wss://your-project.livekit.cloud` |
| `LIVEKIT_API_KEY` | ✅ | LiveKit API key |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit API secret |
| `LIVEKIT_SIP_TRUNK_ID` | ✅ **NEW** | Outbound SIP trunk ID from LiveKit console |
| `MURF_API_KEY` | ✅ | Murf Falcon TTS key |
| `DEEPGRAM_API_KEY` | ✅ | Deepgram STT key |
| `GOOGLE_API_KEY` | ✅ | Gemini LLM key |
| `TWILIO_ACCOUNT_SID` | ⚠️ | For reference / direct Twilio calls |
| `TWILIO_AUTH_TOKEN` | ⚠️ | For reference / direct Twilio calls |
| `TWILIO_FROM_NUMBER` | ⚠️ | Your Twilio caller ID |

---

## Alternative: Linphone (No Twilio Required)

If your Twilio free trial is exhausted, you can use **Linphone** (free SIP softphone):

1. Download Linphone from [linphone.org](https://www.linphone.org)
2. In LiveKit console → SIP → create an **inbound** SIP trunk with a SIP URI
3. In Linphone, register that SIP URI as an account
4. Trigger the call pointing to your Linphone SIP address instead of a phone number:

```powershell
uv run python src/trigger_call.py --number "sip:yourname@your-sip-domain.com"
```

---

## Project Structure

```
day 6/
├── backend/
│   ├── src/
│   │   ├── agent.py           # Voice agent (outbound-aware)
│   │   ├── prompt.py          # System prompt + outbound greeting
│   │   ├── trigger_call.py    # CLI: fire an outbound call
│   │   ├── trigger_server.py  # HTTP API: POST /call
│   │   ├── tools.py           # Agent function tools
│   │   ├── database.py        # User persistence (SQLite)
│   │   └── database_products.py  # Product catalogue (SQLite)
│   ├── data/
│   │   ├── schema.sql
│   │   └── data_seed.sql
│   ├── pyproject.toml
│   ├── .env.example
│   └── .env.local             # ← fill this in
├── frontend/                  # Next.js UI (same as Day 5)
├── start_app.ps1              # Start everything
└── README.md
```

---

## Running Everything at Once

```powershell
cd "day 6"
.\start_app.ps1
```

This opens 3 terminal windows:
1. **Agent** (`uv run python src/agent.py dev`)
2. **Trigger Server** (`uvicorn` on port 8001)
3. **Frontend** (`pnpm dev` on port 3000)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Voice Agent | LiveKit Agents SDK ~1.4 |
| TTS | **Murf Falcon** (fastest TTS API) |
| STT | Deepgram Nova-3 |
| LLM | Google Gemini |
| Telephony | Twilio SIP Trunk ↔ LiveKit SIP |
| Frontend | Next.js + Tailwind CSS |
| Database | SQLite (user memory + product catalogue) |
