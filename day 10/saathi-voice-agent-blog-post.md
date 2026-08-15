# Saathi: building a Kirana store voice agent in 10 days with Murf Falcon

*How I built a Hinglish-speaking voice assistant for local grocery stores — and what ten days of #VoiceForBharat taught me about voice AI.*

## The problem and the users

Most local Kirana (neighbourhood grocery) stores in India still run on phone calls and memory. The shopkeeper remembers what Ramesh usually orders, but there's no system behind that memory — no record of preferences, no way to check stock before promising something, and no help when the owner is busy serving someone else in the shop.

I built **Saathi**, a voice agent for the **Local Commerce** track, to be that missing layer. It's designed for customers who are more comfortable *talking* than typing — especially in Hindi, Hinglish, or a code-mixed version of both — and for a store owner who needs a system that can take routine calls off their hands without ever pretending to be a human or making promises it can't keep.

Voice is the right interface here because it removes the biggest barrier to digital tools in local commerce: literacy and app-navigation friction. If you can make a phone call, you can use Saathi.

## What the voice agent does

Saathi can:

- Hold a natural, code-mixed conversation in English, Hindi, or Hinglish
- Greet returning customers by name and recall their last order, quantity, and delivery slot
- Look up products and check live stock before promising anything
- Place an order and confirm it back to the customer
- Escalate to the store owner — with consent — when something is outside its scope
- Call customers proactively to confirm orders
- Hand off payment disputes and refund requests to a dedicated support specialist agent
- Log every call's outcome to a small analytics dashboard

None of this shipped on day one. Each piece was added deliberately across the ten days, and the sections below walk through how.

## How the system works

At its core, Saathi is a real-time loop: the caller's speech is transcribed, reasoned over, and turned back into speech, all streamed live over [LiveKit](https://docs.livekit.io/agents/).

![The core voice loop: STT to LLM to TTS](blog-assets/pipeline.png)

- **STT** — Deepgram `nova-3`, set to `multi` language mode so it transcribes code-mixed Hindi/English accurately
- **LLM** — Google Gemini `3.5-flash-lite`, which carries the persona, the guardrails, and the tool-calling logic
- **TTS** — Murf Falcon, the fastest TTS API I tested, speaking in the Indian English voice **Anisha** (and **Samar** for the specialist agent, so the handoff is audibly obvious)
- **Transport** — LiveKit handles the real-time audio both from the browser and from phone calls bridged in over SIP

Zooming out, here's how the pieces fit together once memory, tools, telephony, escalation, analytics, and the specialist handoff are all in place:

![Full system architecture of Saathi](blog-assets/architecture.png)

A caller reaches the agent either through the browser frontend or by phone via a Twilio SIP trunk. Both paths land in the same LiveKit room, so the agent logic doesn't need to know or care which channel it's on. From there, the main `Assistant` agent uses its tools against a small SQLite data layer, and can transfer the conversation to a specialist agent when needed.

## The most important features

### An Indian voice, built for code-mixed conversations

The agent speaks in Murf Falcon's **Anisha** voice with the `Conversation` style, and the Deepgram STT model runs in `multi` mode instead of a fixed language — that one setting change is what lets a customer switch from English to Hindi mid-sentence without breaking transcription.

### Memory that survives across calls

Saathi remembers returning customers using a small SQLite-backed profile store, and — critically — only saves anything after the customer has explicitly agreed to it.

![lookup_user and save_user_profile tools](blog-assets/memory_snippet.png)

### Tools that check real data before promising anything

Before the agent confirms an order, it calls a catalogue lookup and a stock check against a local product database. If a customer asks in Hindi, a small translation layer converts common grocery terms (Devanagari script) into the English terms the database understands before it ever runs a query.

![Translating code-mixed queries before hitting the catalogue database](blog-assets/hinglish_snippet.png)

### Escalation with consent, not silence

When a request falls outside what the agent can safely resolve — a payment dispute, a delivery complaint — it doesn't guess or stall. It explains the limitation, asks permission to pass details to the store owner, and only then creates an escalation ticket with a reference ID the caller can quote later. Anything that looks like a password, OTP, or card number is stripped out before the ticket is ever saved.

![create_escalation tool with PII stripped from the summary](blog-assets/escalation_snippet.png)

### Handing off to a specialist

Rather than trying to make one agent good at everything, Saathi hands payment and refund conversations to a **Customer Support Specialist** agent with its own voice (Samar) and its own narrower toolset.

![transfer_to_support: handing the conversation to a specialist agent](blog-assets/handoff_snippet.png)

The specialist receives the full chat history — the customer never has to repeat themselves — and the voice change makes the handoff audibly clear rather than a silent, confusing swap.

### Outbound calls and a call analytics dashboard

Saathi can also dial out, for example to confirm a pending order, and every call — inbound or outbound, browser or phone — is logged when it ends. A call counts as a **success** only if an order was actually placed; everything else is logged as a non-conversion. That distinction feeds a small dashboard showing total, successful, and failed calls, without exposing any caller's personal details.

## The difficult parts

**Code-mixed language was harder than expected.** Getting Hinglish to transcribe well took two changes, not one: setting Deepgram's language to `multi` so STT didn't force everything into a single language, and adding a translation step so Devanagari product names (say, आटा) resolved correctly against an English-only product database. Neither change alone was enough — it took both.

**Getting the LLM to actually ask permission, every time.** Early on, the agent would sometimes save customer data or escalate an issue without clearly asking first. The fix wasn't more code — it was making the system prompt explicit and mechanical about consent ("ONLY call this tool AFTER the customer has clearly said yes"), and putting that same instruction directly inside the tool's docstring, since the LLM reads both.

**Preserving context across a handoff.** The first version of the specialist handoff lost conversation history, so customers had to repeat their whole problem to the new agent. Passing a copy of the chat context (`chat_ctx.copy(exclude_instructions=True)`) into the specialist agent's constructor fixed this — the specialist inherits everything the customer already said, minus the main agent's system instructions.

## Build your own voice agent

If you want to build something similar, here's what you need, and the shape it takes in this codebase.

**The four core components:**

1. **Speech-to-text (STT)** — converts the caller's audio into text. This project uses Deepgram.
2. **An LLM** — reasons over the transcript, holds the persona and guardrails, and decides when to call a tool. This project uses Google Gemini.
3. **Text-to-speech (TTS)** — turns the LLM's reply back into audio. This project uses **Murf Falcon**, chosen specifically for its speed and its Indian-language voice options.
4. **Real-time transport** — moves audio both directions with low latency. This project uses LiveKit, which also handles browser and SIP (phone) participants through the same interface.

**Setting up and running the project:**

```bash
# Backend
cd backend
uv sync
cp .env.example .env.local        # fill in your API keys here — never commit this file
uv run python src/agent.py download-files
uv run python src/agent.py console   # test in your terminal, no frontend needed
uv run python src/agent.py dev       # or run in dev mode with the frontend

# Frontend
cd frontend
pnpm install
pnpm dev
```

**Where API keys go:** all secrets live in `backend/.env.local`, which is git-ignored and created from `backend/.env.example`. You'll need keys for LiveKit, Murf, Deepgram, and Google — none of them are ever hard-coded or committed.

**Connecting and testing a conversation:** the fastest way to sanity-check your agent is `uv run python src/agent.py console`, which gives you a conversation in your terminal with no frontend required. Once that works, run the frontend and the agent in dev mode together, open the local URL, and start talking.

## What I'd improve next

- Move from SQLite to a hosted database so state survives redeploys and scales past a single store
- Add streaming partial-result display on the frontend so users can see the transcript as they speak, not just after
- Expand the specialist roster — a delivery-tracking specialist would be a natural next addition alongside the support one

## Code and demos

The full project — every day's changes, from the first working conversation to the multi-agent handoff — is public here:

**Repository:** https://github.com/JatinKevlani/murf-livekit-starter

(Please make sure the repo is set to public before publishing your post, and double-check that no real phone numbers, `.env.local` files, or caller data are committed anywhere in the history.)

---

*This post covers 10 Days of Voice Agents — VoiceForBharat Edition. Built with Murf Falcon, the fastest TTS API, on top of the [Murf LiveKit starter](https://github.com/murf-ai/murf-livekit-starter).*
