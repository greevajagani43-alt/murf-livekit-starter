import logging

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

import db

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Change this prompt to change what your voice agent does.
# See README.md for example prompts (customer support, language tutor, receptionist).
SYSTEM_PROMPT = """You are a friendly and efficient assistant for a local Kirana store (local commerce shop). Help users with their shopping list, tell them about available products, and take their orders. The user may speak in Hindi or English, but you must always reply in Hindi. Keep your responses concise, natural, and helpful. Do not use complex formatting, emojis, or symbols.

When a user calls, politely ask for their name first to check if they are a returning customer.
Use the `lookup_caller` tool to check their details.
If they are a returning customer, greet them warmly by their name and mention their past preferences (e.g., "Namaste Ramesh, last time you ordered rice. Do you need the same quantity today?").
During the conversation, pay attention to facts like their past orders, usual quantities, and preferred delivery slot.
BEFORE saving any information, you MUST ask the user if it's okay to remember these details for their next visit.
If they say yes, use the `save_caller_info` tool to save their details. If they say no, do NOT save the information.

LANGUAGE & SCRIPT
Always write every language in its own native script.
- Hindi → Devanagari (नमस्ते), never romanized (never "namaste").
- Same rule for all non-English languages.
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    @function_tool
    async def lookup_caller(self, context: RunContext, name: str) -> str:
        """Use this tool to look up a caller by their name.
        Call this tool when the user provides their name to check if they are a returning customer.

        Args:
            name: The caller's name to look up.
        """
        logger.info(f"Looking up caller with name: {name}")
        user = db.get_user(name)
        if user:
            return f"Found user: {user['name']}. Facts: {user['facts']}"
        return "User not found."

    @function_tool
    async def save_caller_info(
        self,
        context: RunContext,
        name: str,
        past_orders: str,
        usual_quantities: str,
        preferred_delivery_slot: str,
    ) -> str:
        """Use this tool to save a caller's information.
        You MUST ask for their permission before saving this information.

        Args:
            name: The caller's name.
            past_orders: Summary of past orders (e.g., 'rice, dal').
            usual_quantities: Summary of usual quantities (e.g., '5kg rice, 2kg dal').
            preferred_delivery_slot: Preferred delivery time (e.g., 'evening', 'morning').
        """
        logger.info(f"Saving info for caller: {name}")
        facts = {
            "past_orders": past_orders,
            "usual_quantities": usual_quantities,
            "preferred_delivery_slot": preferred_delivery_slot,
        }
        db.save_user(name, facts)
        return "Caller information saved successfully."


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Initialize the database
    db.init_db()

    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3", language="multi"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
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

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
