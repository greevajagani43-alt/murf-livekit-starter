"""
agent.py  —  Ratan Kirana Voice Agent (Saathi)
───────────────────────────────────────────────
Day 5 refactor: tools extracted to tools.py, prompt to prompt.py,
product DB helpers to database_products.py.
Day 8: Added call analytics tracking — records outcome of every call.
"""

import logging
import re
import time
from typing import Optional

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from database import init_database
from database_calls import init_calls_db, record_call
from database_escalations import init_escalations_db
from database_orders import init_orders_db
from database_products import init_products_db
from prompt import SYSTEM_PROMPT
from tools import (
    check_stock,
    create_escalation,
    lookup_catalogue,
    lookup_user,
    place_order,
    save_user_profile,
)
from livekit.agents import RunContext, function_tool, ChatContext

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")


from prompt import SYSTEM_PROMPT, CUSTOMER_SUPPORT_PROMPT

# ── Customer Support Specialist ────────────────────────────────────────────


class CustomerSupportSpecialist(Agent):
    """Specialist agent for handling refunds, disputes, and escalations."""

    def __init__(self, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=CUSTOMER_SUPPORT_PROMPT,
            chat_ctx=chat_ctx,
            tools=[create_escalation],
            tts=murf.TTS(
                voice="Samar",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True,
            ),
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="Introduce yourself by saying 'Hi, I'm the customer care specialist.' and ask how you can help with their issue."
        )


# ── Assistant ──────────────────────────────────────────────────────────────


class Assistant(Agent):
    """Saathi — Ratan Kirana voice assistant."""

    def __init__(self, user_id: str = "unknown") -> None:
        instructions = SYSTEM_PROMPT.format(user_id=user_id)
        super().__init__(
            instructions=instructions,
            # Attach tools from tools.py
            tools=[
                lookup_user,
                save_user_profile,
                lookup_catalogue,
                check_stock,
                place_order,
            ],
        )

    @function_tool()
    async def transfer_to_support(self, context: RunContext) -> tuple[Agent, str]:
        """Transfer the user to the customer support specialist for payment disputes, refund requests, or order issues."""
        support_agent = CustomerSupportSpecialist(
            chat_ctx=self.chat_ctx.copy(exclude_instructions=True)
        )
        return support_agent, "Transferring you to our customer support specialist."


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
    logger.info("Initialising calls database…")
    init_calls_db()
    logger.info("Loading VAD model…")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarm complete.")


server.setup_fnc = prewarm


# ── Helpers ────────────────────────────────────────────────────────────────


def extract_user_id_from_room(room_name: str) -> Optional[str]:
    """Extract user_id from room name (format: voice_assistant_room_USER_ID)."""
    match = re.search(r"voice_assistant_room_(.+)", room_name)
    return match.group(1) if match else None


def detect_channel(room: rtc.Room) -> str:
    """Detect whether this is a browser or SIP call."""
    for p in room.remote_participants.values():
        if p.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            return "sip"
    return "browser"


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

    # Day 8: Track call start time and initialise analytics state
    call_start_time = time.time()
    session.custom_data = {"order_placed": False}

    # Day 8: Record call outcome when session closes
    @session.on("close")
    def on_session_close(*args):
        try:
            duration = int(time.time() - call_start_time)
            channel = detect_channel(ctx.room)
            order_placed = getattr(session, "custom_data", {}).get(
                "order_placed", False
            )

            if order_placed:
                outcome = "success"
                failure_reason = None
            else:
                outcome = "failed"
                failure_reason = "no_order"

            call_id = f"CALL-{ctx.room.name}-{int(call_start_time)}"

            record_call(
                call_id=call_id,
                user_id=user_id,
                outcome=outcome,
                channel=channel,
                failure_reason=failure_reason,
                duration_seconds=duration,
            )
            logger.info(
                "Call analytics recorded: %s outcome=%s duration=%ds",
                call_id,
                outcome,
                duration,
            )
        except Exception as exc:
            logger.error("Failed to record call analytics: %s", exc)

    await session.start(
        agent=Assistant(user_id=user_id),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
