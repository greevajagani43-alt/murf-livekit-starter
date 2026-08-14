"""
agent.py  —  Saathi Voice Agent (Ratan Kirana Store)
──────────────────────────────────────────────────────
Day 7: Full Day 6 agent restored with outbound call support,
SIP telephony detection, Murf Falcon TTS, escalation tools,
and all Day 7 capabilities merged.

Pipeline:  Deepgram Nova-3 STT → Gemini LLM → Murf Falcon TTS
Telephony: LiveKit SIP Trunk → Twilio → Customer's phone
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Fix Windows console Unicode encoding for Hindi/multilingual log output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    tokenize,
    room_io,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from database import init_database
from database_escalations import init_escalations_db
from database_orders import init_orders_db
from database_products import init_products_db
from prompt import SYSTEM_PROMPT, OUTBOUND_GREETING
from tools import (
    lookup_user,
    save_user_profile,
    lookup_catalogue,
    check_stock,
    place_order,
    create_escalation,
)

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

load_dotenv(Path(__file__).parent.parent / ".env.local")


# ── Assistant ──────────────────────────────────────────────────────────────


class Assistant(Agent):
    """Saathi — Ratan Kirana outbound/inbound voice assistant."""

    def __init__(self, user_id: str = "unknown", is_outbound: bool = False) -> None:
        instructions = SYSTEM_PROMPT.format(
            user_id=user_id,
            outbound_context="OUTBOUND_CALL" if is_outbound else "INBOUND_CALL",
        )
        super().__init__(
            instructions=instructions,
            tools=[
                lookup_user,
                save_user_profile,
                lookup_catalogue,
                check_stock,
                place_order,
                create_escalation,
            ],
        )
        self._is_outbound = is_outbound

    async def on_enter(self) -> None:
        """Speak outbound greeting immediately when call connects."""
        if self._is_outbound and hasattr(self, "session") and self.session:
            await self.session.say(OUTBOUND_GREETING, allow_interruptions=True)


# ── Server setup ───────────────────────────────────────────────────────────

server = AgentServer()


def prewarm(proc: JobProcess):
    """Prewarm models and initialise databases."""
    logger.info("Initialising user database…")
    init_database()
    logger.info("Initialising products database…")
    init_products_db()
    logger.info("Initialising orders database…")
    init_orders_db()
    logger.info("Initialising escalations database…")
    init_escalations_db()
    logger.info("Loading VAD model…")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarm complete.")


server.setup_fnc = prewarm


# ── Helpers ────────────────────────────────────────────────────────────────


def extract_user_id_from_room(room_name: str) -> Optional[str]:
    """Extract user_id from room name (format: saathi_outbound_USERID or voice_assistant_room_USERID)."""
    match = re.search(r"(?:saathi_outbound_|voice_assistant_room_)(.+)", room_name)
    return match.group(1) if match else None


def is_sip_participant(participant: rtc.Participant) -> bool:
    """Return True if this participant came in via SIP (phone call)."""
    return participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP


# ── Session entry point ────────────────────────────────────────────────────


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    await ctx.connect()

    # Detect whether this is an outbound/SIP call or a browser call
    is_outbound = "saathi_outbound" in ctx.room.name
    remote_participants = list(ctx.room.remote_participants.values())
    if remote_participants:
        first = remote_participants[0]
        if is_sip_participant(first):
            is_outbound = True
        logger.info(
            "Participant kind=%s  is_outbound=%s", first.kind, is_outbound
        )

    user_id = extract_user_id_from_room(ctx.room.name) or "unknown"

    ctx.log_context_fields = {
        "room": ctx.room.name,
        "user_id": user_id,
        "is_outbound": is_outbound,
    }

    logger.info(
        "Starting session  room=%s  user_id=%s  outbound=%s",
        ctx.room.name, user_id, is_outbound,
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-2.5-flash-lite"),
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            pitch=10,
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(user_id=user_id, is_outbound=is_outbound),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    # Use telephony-grade noise cancellation for SIP/phone calls
                    noise_cancellation.BVCTelephony()
                    if is_sip_participant(params.participant)
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    if is_outbound:
        logger.info(
            "Outbound call detected — speaking greeting: %s", OUTBOUND_GREETING
        )
        await session.say(OUTBOUND_GREETING, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(server)
