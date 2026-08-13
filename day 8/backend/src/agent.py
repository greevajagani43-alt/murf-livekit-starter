"""
agent.py  —  Saathi Voice Agent (Day 8: Voice Agent Performance Dashboard)
─────────────────────────────────────────────────────────────────────────────
Day 8 (Local Commerce Track):
- Tracks every browser and SIP call outcome automatically.
- Deterministic success criteria: Call is marked 'successful' when the caller
  completes a product enquiry/search. Otherwise marked 'failed'.
- Saves call metrics (call_id, call_type, duration, outcome, reason) into SQLite DB.
- Powered by Murf Falcon TTS, Deepgram STT, and Google Gemini LLM.
"""

import asyncio
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Fix Windows console Unicode encoding
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
    function_tool,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

sys.path.insert(0, str(Path(__file__).parent))

from database_calls import init_calls_db, record_call_end, record_call_start
from products_db import PRODUCTS_CATALOGUE, search_products
from prompt import SYSTEM_PROMPT

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

load_dotenv(Path(__file__).parent.parent / ".env.local")


# ── Function Tools for Local Commerce Enquiry ──────────────────────────────


def _get_agent_instance(context: RunContext):
    """Safely retrieve Assistant instance from RunContext across livekit-agents versions."""
    if hasattr(context, "session") and hasattr(context.session, "agent"):
        return context.session.agent
    return getattr(context, "agent", None)


@function_tool
async def search_product_catalogue(
    context: RunContext,
    query: str,
) -> str:
    """Search Ratan Kirana product catalogue for pricing, availability, and details.
    
    Args:
        query: Name of item (e.g. 'headphones', 'atta', 'oil', 'milk', 'rice', 'dal', 'salt')
    """
    results = search_products(query)
    # Mark product enquiry as completed on assistant instance
    agent_instance = _get_agent_instance(context)
    if agent_instance and hasattr(agent_instance, "mark_enquiry_completed"):
        agent_instance.mark_enquiry_completed(f"Searched product: {query}")

    if not results:
        return f"No exact match found for '{query}'. Available items include: Headphones, Atta, Rice, Dal, Milk, Oil, Salt."

    formatted = []
    for p in results:
        status = "In Stock" if p["in_stock"] else "Out of Stock"
        formatted.append(f"{p['name']} ({p['unit']}): Rs.{p['price']} [{status}] - {p['description']}")

    return "\n".join(formatted)


@function_tool
async def list_all_products(
    context: RunContext,
) -> str:
    """Get the full list of products available at Ratan Kirana Store."""
    agent_instance = _get_agent_instance(context)
    if agent_instance and hasattr(agent_instance, "mark_enquiry_completed"):
        agent_instance.mark_enquiry_completed("Listed catalogue products")

    formatted = [
        f"• {p['name']} ({p['unit']}): Rs.{p['price']} [{'In Stock' if p['in_stock'] else 'Out of Stock'}]"
        for p in PRODUCTS_CATALOGUE
    ]
    return "Products available at Ratan Kirana Store:\n" + "\n".join(formatted)


# ── Assistant Class ─────────────────────────────────────────────────────────


class Assistant(Agent):
    """Saathi — Day 8 Local Commerce Voice Assistant with outcome tracking."""

    def __init__(self, call_id: str, call_type: str = "browser") -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[search_product_catalogue, list_all_products],
        )
        self.call_id = call_id
        self.call_type = call_type
        self.enquiry_completed = False
        self.enquiry_reason = "Call ended before completing product enquiry"

    def mark_enquiry_completed(self, reason: str) -> None:
        """Called when user successfully completes a product enquiry."""
        self.enquiry_completed = True
        self.enquiry_reason = reason
        logger.info("[Agent %s] Enquiry marked completed: %s", self.call_id, reason)


# ── Server Setup ────────────────────────────────────────────────────────────

server = AgentServer()


def prewarm(proc: JobProcess):
    """Prewarm models and database."""
    logger.info("Initializing Day 8 calls database...")
    init_calls_db()
    logger.info("Loading VAD model...")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Prewarm complete.")


server.setup_fnc = prewarm


def is_sip_participant(participant: rtc.Participant) -> bool:
    """Return True if participant connected via SIP trunk."""
    return participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    await ctx.connect()

    # Determine call ID and call type
    call_id = ctx.room.name or f"call_{int(datetime.utcnow().timestamp())}"
    call_type = "browser"

    remote_participants = list(ctx.room.remote_participants.values())
    if remote_participants and is_sip_participant(remote_participants[0]):
        call_type = "sip"

    logger.info("New call starting: call_id=%s, type=%s", call_id, call_type)

    # 1. Record Call Start in Database
    record_call_start(call_id=call_id, call_type=call_type)
    started_at = datetime.utcnow()

    # Instantiate assistant
    assistant = Assistant(call_id=call_id, call_type=call_type)

    # Build pipeline with Murf Falcon TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-3.6-flash"),
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

    try:
        await session.start(
            agent=assistant,
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=lambda params: (
                        noise_cancellation.BVCTelephony()
                        if is_sip_participant(params.participant)
                        else noise_cancellation.BVC()
                    ),
                ),
            ),
        )

        # Greet caller upon connection
        await session.say(
            "Namaste! Welcome to Ratan Kirana Store. How can I help you today?",
            allow_interruptions=True,
        )

        # Wait until participant disconnects or room closes
        disconnect_event = asyncio.Event()

        @ctx.room.on("participant_disconnected")
        def _on_participant_disconnected(p):
            disconnect_event.set()

        @ctx.room.on("disconnected")
        def _on_room_disconnected(*args):
            disconnect_event.set()

        await disconnect_event.wait()
    except Exception as e:
        logger.error("Session runtime error for call %s: %s", call_id, e)
    finally:
        # 2. Record Call End and Determine Outcome (Successful / Failed)
        ended_at = datetime.utcnow()
        duration = int((ended_at - started_at).total_seconds())

        if assistant.enquiry_completed:
            outcome = "successful"
            reason = f"SUCCESS: {assistant.enquiry_reason}"
        else:
            outcome = "failed"
            reason = f"FAILED: {assistant.enquiry_reason}"

        logger.info(
            "Call finished: call_id=%s, type=%s, duration=%ds, outcome=%s, reason=%s",
            call_id,
            call_type,
            duration,
            outcome,
            reason,
        )

        record_call_end(
            call_id=call_id,
            outcome=outcome,
            reason=reason,
            duration=duration,
            ended_at=ended_at.isoformat(),
        )


if __name__ == "__main__":
    cli.run_app(server)
