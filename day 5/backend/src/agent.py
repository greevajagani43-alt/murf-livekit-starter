"""
agent.py  —  Ratan Kirana Voice Agent (Saathi)
───────────────────────────────────────────────
Day 5 refactor: tools extracted to tools.py, prompt to prompt.py,
product DB helpers to database_products.py.
"""

import logging
import re
from typing import Optional

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

from database import init_database, update_last_interaction
from database_products import init_products_db
from prompt import SYSTEM_PROMPT
from tools import lookup_user, save_user_profile, lookup_catalogue, check_stock

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")


# ── Assistant ──────────────────────────────────────────────────────────────


class Assistant(Agent):
    """Saathi — Ratan Kirana voice assistant."""

    def __init__(self, user_id: str = "unknown") -> None:
        instructions = SYSTEM_PROMPT.format(user_id=user_id)
        super().__init__(
            instructions=instructions,
            # Attach all tools from tools.py
            tools=[lookup_user, save_user_profile, lookup_catalogue],
        )


# ── Server setup ───────────────────────────────────────────────────────────

server = AgentServer()


def prewarm(proc: JobProcess):
    """Prewarm models and initialise databases."""
    logger.info("Initialising user database…")
    init_database()
    logger.info("Initialising products database…")
    init_products_db()
    logger.info("Loading VAD model…")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarm complete.")


server.setup_fnc = prewarm


# ── Helpers ────────────────────────────────────────────────────────────────


def extract_user_id_from_room(room_name: str) -> Optional[str]:
    """Extract user_id from room name (format: voice_assistant_room_USER_ID)."""
    match = re.search(r"voice_assistant_room_(.+)", room_name)
    return match.group(1) if match else None


# ── Session entry point ────────────────────────────────────────────────────


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    user_id = extract_user_id_from_room(ctx.room.name) or "unknown"

    ctx.log_context_fields = {
        "room": ctx.room.name,
        "user_id": user_id,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-3.5-flash-lite"),
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(user_id=user_id),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
