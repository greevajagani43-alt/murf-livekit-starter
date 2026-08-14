# Day 6 Task — Outbound Calls

## Objective

Make the Saathi agent place **outbound calls** to customers' phones proactively,
using **Twilio SIP Trunk** integrated via **LiveKit SIP**.

---

## Track: Local Commerce

**Use case:** Ratan Kirana Store's Saathi agent calls customers when their usual
grocery items are due for a restock (e.g., Atta, Toor Dal, Oil).

---

## Steps

### ✅ Step 1 — Outbound Use Case

**Trigger:** Customer's usual restock day arrives based on past order patterns.

**Call reason:** "आपका आटा फिर से मँगाने का वक़्त आ गया है।"
*(Your atta is due for restocking.)*

---

### ✅ Step 2 — Telephony Integration

**Architecture:**
```
trigger_call.py  →  LiveKit SIP API  →  Twilio SIP Trunk  →  Customer Phone
                         ↕
               agent.py (Murf Falcon TTS + Deepgram STT + Gemini LLM)
```

**New files added:**
- `backend/src/trigger_call.py` — CLI to fire a call
- `backend/src/trigger_server.py` — HTTP `POST /call` endpoint
- `backend/src/agent.py` — Updated to detect SIP participants + speak greeting

**New env var:** `LIVEKIT_SIP_TRUNK_ID`

---

### ✅ Step 3 — Agent Calls and Completes Interaction

The agent:
1. Detects it's a phone call (SIP participant kind)
2. Uses `BVCTelephony` noise cancellation for phone audio quality
3. Speaks the outbound greeting immediately on connect
4. Handles the order flow (lookup_user → check_stock → confirm order)
5. Respects opt-out phrases and ends the call cleanly

---

### ✅ Step 4 — Proper Outbound Opening

First 2 sentences (spoken immediately on connect):

> **"नमस्ते! मैं साथी हूँ, रतन किराना स्टोर की तरफ़ से बोल रहा हूँ।**
> **आपका आटा फिर से मँगाने का वक़्त आ गया है — अगर बात नहीं करनी**
> **तो बस कह दीजिए 'नहीं चाहिए' और मैं कॉल बंद कर दूँगा।"**

| Requirement | ✅ Met by |
|-------------|----------|
| Who's calling | "मैं साथी हूँ, रतन किराना स्टोर की तरफ़ से" |
| Why calling | "आपका आटा फिर से मँगाने का वक़्त आ गया है" |
| How to stop | "बस कह दीजिए 'नहीं चाहिए'" |

---

### ⬜ Step 5 — Record Video

Record a short video of:
- Your phone ringing
- Picking up the call
- Saathi speaking the outbound greeting
- A short interaction (e.g., confirming a restock order)

---

### ⬜ Step 6 — LinkedIn Post

Post the video on LinkedIn mentioning:
- What you built on Day 6
- That you're using **Murf Falcon** (fastest TTS API)
- That you're part of **10 Days of Voice Agents**
- Tag the official **Murf AI** handle
- Hashtag: **#VoiceForBharat**

---

### ⬜ Step 7 — Submit

Submit your LinkedIn post link at the submission form with your name and email.

---

## How to Run

```powershell
# 1. Install deps (one time)
cd "day 6\backend"
uv sync

# 2. Download model files (one time)
uv run python src/agent.py download-files

# 3. Start the agent
uv run python src/agent.py dev

# 4. Trigger a call (in another terminal)
uv run python src/trigger_call.py --number +91XXXXXXXXXX --name "Your Name"
```

## How to Test (No Phone Call)

```powershell
# Dry run — prints config only, no real call
uv run python src/trigger_call.py --number +91XXXXXXXXXX --dry-run

# Run unit tests
uv run pytest tests/
```
