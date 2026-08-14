"""
uk_agent.py — UK Delivery Confirmation Agent
─────────────────────────────────────────────
Calls customers one day before delivery to confirm their presence.

Run the worker:
    uv run python src/telephony/outbound/uk_agent.py dev

Trigger a call for a specific order:
    uv run python src/telephony/outbound/dial.py \
        --to kavan \
        --name "Kavan" \
        --reason delivery_confirmation \
        --metadata '{"order_id": "ORD-20260811-001"}'

Or trigger all tomorrow's deliveries:
    uv run python src/telephony/outbound/trigger_delivery_calls.py
"""

import asyncio
import json
import logging
import os
import sys

from dotenv import load_dotenv
from livekit import api, rtc
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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database_orders import (
    init_orders_db,
    get_order_by_id,
    update_delivery_confirmation,
)

logger = logging.getLogger("uk-agent")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

OUTBOUND_TRUNK_ID = os.getenv("LIVEKIT_SIP_OUTBOUND_TRUNK_ID")
CALLEE_IDENTITY = "phone-user"

# ── UK Agent System Prompt ─────────────────────────────────────────────────

UK_AGENT_PROMPT = """
IDENTITY

You are Saathi, the voice assistant for Ratan Kirana & General Store in Ahmedabad.
You are making a DELIVERY CONFIRMATION call to a customer named {customer_name}.

STORE INFORMATION
Name: Ratan Kirana & General Store
Location: Maninagar, Ahmedabad
Timings: 8 AM to 10 PM every day
Contact: 098250-XXXXX

CALL PURPOSE
You are calling because the customer has an order scheduled for delivery TOMORROW.
Your job is to confirm that someone will be home to receive the delivery.

ORDER DETAILS
Order ID: {order_id}
Items: {items_summary}
Total Amount: ₹{total_amount}
Delivery Address: {delivery_address}
Delivery Slot: {delivery_slot}

CONVERSATION FLOW

1. GREETING
   Start by greeting the customer warmly by name.
   Identify yourself and the store.
   State clearly why you're calling.

   Example in Hindi:
   "नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। कल आपके ऑर्डर की डिलीवरी है, इसलिए कॉल कर रही हूँ।"

   Example in English:
   "Hello {customer_name}! This is Saathi from Ratan Kirana Store. I'm calling about your delivery scheduled for tomorrow."

2. CONFIRM THE ORDER
   Summarize what they ordered briefly.

   Example in Hindi:
   "आपने {items_summary} ऑर्डर किया है, कुल ₹{total_amount} का।"

   Example in English:
   "You ordered {items_summary}, total ₹{total_amount}."

3. CONFIRM DELIVERY ADDRESS
   Read back the delivery address and ask if it's correct.

   Example in Hindi:
   "डिलीवरी का पता {delivery_address} है। क्या यह सही है?"

   Example in English:
   "The delivery address is {delivery_address}. Is that correct?"

4. ASK ABOUT PRESENCE
   Ask if someone will be home tomorrow to receive the delivery.

   Example in Hindi:
   "कल {delivery_slot} के समय कोई घर पर होगा डिलीवरी लेने के लिए?"

   Example in English:
   "Will someone be home tomorrow during the {delivery_slot} to receive the delivery?"

5. HANDLE RESPONSES

   IF YES — They confirm they'll be home:
   - Thank them warmly
   - Confirm the delivery slot one more time
   - Say goodbye

   Example in Hindi:
   "बहुत अच्छा! तो कल {delivery_slot} में डिलीवरी आ जाएगी। धन्यवाद, आपका दिन शुभ हो!"

   Example in English:
   "Great! The delivery will arrive tomorrow during the {delivery_slot}. Thank you, have a wonderful day!"

   IF NO — They won't be home:
   - Ask when would be a good time
   - Offer to reschedule the delivery
   - Note their preferred time

   Example in Hindi:
   "कोई बात नहीं। आप किस समय घर पर होंगे? हम डिलीवरी का समय बदल सकते हैं।"

   Example in English:
   "No problem. When would be a good time? We can reschedule the delivery."

   IF ADDRESS IS WRONG:
   - Ask for the correct address
   - Note the new address
   - Say you'll update the order

   Example in Hindi:
   "कृपया मुझे सही पता बताएं। मैं ऑर्डर में अपडेट कर दूंगी।"

   Example in English:
   "Please give me the correct address. I'll update the order."

   IF THEY WANT TO CANCEL:
   - Confirm cancellation politely
   - Say you'll process it
   - Thank them anyway

   Example in Hindi:
   "ठीक है, मैं आपका ऑर्डर कैंसिल कर देती हूँ। अगर भविष्य में कुछ चाहिए तो ज़रूर बताइएगा।"

   Example in English:
   "Alright, I'll cancel your order. Please do reach out if you need anything in the future."

6. END THE CALL
   Always end with a warm goodbye.

   Example in Hindi:
   "धन्यवाद! रतन किराना स्टोर से आपका दिन शुभ हो!"

   Example in English:
   "Thank you! Have a great day from Ratan Kirana Store!"

IMPORTANT RULES

1. Be warm and friendly — this is a courtesy call, not a sales call.
2. Keep it brief — the call should take 1-2 minutes max.
3. If the customer seems busy, ask if it's a good time and offer to call back.
4. Never be pushy or aggressive.
5. Always confirm the delivery address before ending.
6. If the customer doesn't answer, leave a brief voicemail with the order ID and callback number.
7. Use the customer's language — match Hindi or English based on what they speak.

GUARDRAILS
- Never ask for OTP, PIN, bank details, or payment information.
- Never give medical, legal, or financial advice.
- If the customer complains about quality or service, apologize and say someone from the store will call back.

LANGUAGE & SCRIPT
CRITICAL: Always match the customer's language.
Hindi → Devanagari (नमस्ते), never romanized.
English → Latin script (Hello).
Gujarati → Gujarati script (નમસ્તે).

STYLE
Use short sentences under 20 words.
Speak naturally like a helpful neighbor.
Be warm and friendly but professional.
Do not use bullet points, markdown, or technical language.
"""


def build_items_summary(items: list) -> str:
    """Build a human-readable summary of ordered items.

    Args:
        items: List of {product_name, qty, price} dicts

    Returns:
        String like "2 Aashirvaad Atta 5kg aur 1 Amul Butter 100g"
    """
    if not items:
        return "kuch items"

    parts = []
    for item in items:
        name = item["product_name"]
        qty = item["qty"]
        if qty == 1:
            parts.append(name)
        else:
            parts.append(f"{qty} {name}")

    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} और {parts[1]}"
    else:
        return ", ".join(parts[:-1]) + f", और {parts[-1]}"


class UKAgent(Agent):
    """UK Delivery Confirmation Agent for Ratan Kirana Store."""

    def __init__(self, ctx: JobContext, order_data: dict) -> None:
        self.ctx = ctx
        self.order_data = order_data

        customer_name = order_data["customer_name"]
        items_summary = build_items_summary(order_data["items"])

        instructions = UK_AGENT_PROMPT.format(
            customer_name=customer_name,
            order_id=order_data["order_id"],
            items_summary=items_summary,
            total_amount=int(order_data["total_amount"]),
            delivery_address=order_data["delivery_address"],
            delivery_slot=order_data["delivery_slot"],
        )

        super().__init__(
            instructions=instructions,
            tools=[
                self.confirm_delivery,
                self.reschedule_delivery,
                self.cancel_order_from_call,
                self.end_call,
                self.detected_answering_machine,
            ],
        )

    @function_tool
    async def confirm_delivery(self, context: RunContext) -> str:
        """Mark the delivery as confirmed — customer will be home.

        Call this when the customer confirms they'll be home for the delivery.
        """
        order_id = self.order_data["order_id"]
        logger.info(f"Delivery confirmed for order {order_id}")

        success = update_delivery_confirmation(
            order_id=order_id,
            status=1,  # confirmed
            notes="Customer confirmed they'll be home",
        )

        if success:
            return "Delivery confirmed. Thank the customer and end the call warmly."
        else:
            return "Could not update the confirmation. Apologize and say someone will call back."

    @function_tool
    async def reschedule_delivery(
        self, context: RunContext, new_date: str, new_slot: str, reason: str
    ) -> str:
        """Reschedule the delivery when customer can't be home.

        Args:
            new_date: The new delivery date (YYYY-MM-DD)
            new_slot: The new time slot (morning, afternoon, evening)
            reason: Why they need to reschedule
        """
        order_id = self.order_data["order_id"]
        logger.info(f"Rescheduling order {order_id} to {new_date} {new_slot}")

        success = update_delivery_confirmation(
            order_id=order_id,
            status=2,  # rescheduled
            notes=f"Rescheduled to {new_date} {new_slot}. Reason: {reason}",
        )

        if success:
            return f"Delivery rescheduled to {new_date} {new_slot}. Confirm with customer and end the call."
        else:
            return "Could not reschedule. Apologize and say someone will call back."

    @function_tool
    async def cancel_order_from_call(self, context: RunContext) -> str:
        """Cancel the order when customer requests it during the confirmation call."""
        order_id = self.order_data["order_id"]
        logger.info(f"Customer requested cancellation of order {order_id}")

        from database_orders import update_order_status

        success = update_order_status(order_id, "cancelled")

        if success:
            update_delivery_confirmation(
                order_id=order_id,
                status=2,
                notes="Customer cancelled during delivery confirmation call",
            )
            return "Order cancelled. Thank the customer politely and end the call."
        else:
            return "Could not cancel. Apologize and say someone will call back."

    @function_tool
    async def detected_answering_machine(self, context: RunContext) -> str:
        """Hang up because the call reached voicemail.

        Leave a brief message with the store name and callback number.
        """
        logger.info(f"Voicemail detected for order {self.order_data['order_id']}")

        update_delivery_confirmation(
            order_id=self.order_data["order_id"],
            status=3,  # no_answer
            notes="Reached voicemail — left message",
        )

        await self._hangup()
        return "Call ended."

    @function_tool
    async def end_call(self, context: RunContext) -> str:
        """Hang up the call after saying goodbye."""
        logger.info(f"Ending call for order {self.order_data['order_id']}")

        await context.session.generate_reply(
            instructions=(
                "Say a warm goodbye. If speaking Hindi: "
                "'धन्यवाद! रतन किराना स्टोर से आपका दिन शुभ हो!' "
                "If English: 'Thank you! Have a great day from Ratan Kirana Store!'"
            )
        )

        await self._hangup()
        return "Call ended."

    async def _hangup(self) -> None:
        """Delete the room to end the call."""
        try:
            await self.ctx.api.room.delete_room(
                api.DeleteRoomRequest(room=self.ctx.room.name)
            )
        except Exception:
            logger.exception("Failed to delete room")


# ── Server Setup ───────────────────────────────────────────────────────────

server = AgentServer()


def prewarm(proc: JobProcess):
    """Initialize databases and load VAD model."""
    logger.info("Initializing orders database…")
    init_orders_db()

    from database_orders import seed_orders_if_empty

    seed_orders_if_empty()

    logger.info("Loading VAD model…")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("UK Agent prewarm complete.")


server.setup_fnc = prewarm


# ── Session Entry Point ────────────────────────────────────────────────────


@server.rtc_session(agent_name="uk-agent")
async def uk_agent_session(ctx: JobContext):
    """Handle a UK delivery confirmation call."""

    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "uk-agent",
    }

    # Parse metadata from dispatch
    metadata = ctx.job.metadata
    if not metadata:
        logger.error("No metadata in dispatch — need order_id")
        ctx.shutdown()
        return

    try:
        dispatch_data = json.loads(metadata)
    except json.JSONDecodeError:
        logger.error(f"Invalid metadata JSON: {metadata}")
        ctx.shutdown()
        return

    order_id = dispatch_data.get("order_id")
    if not order_id:
        logger.error("No order_id in dispatch metadata")
        ctx.shutdown()
        return

    # Look up the order from the database
    order_data = get_order_by_id(order_id)
    if not order_data:
        logger.error(f"Order not found: {order_id}")
        ctx.shutdown()
        return

    customer_name = order_data["customer_name"]
    customer_phone = order_data["customer_phone"]

    logger.info(
        "UK delivery confirmation — Order: %s, Customer: %s, Phone: %s, Delivery: %s",
        order_id,
        customer_name,
        customer_phone,
        order_data["delivery_date"],
    )

    if not OUTBOUND_TRUNK_ID:
        logger.error("LIVEKIT_SIP_OUTBOUND_TRUNK_ID not set")
        ctx.shutdown()
        return

    await ctx.connect()

    # Same voice pipeline
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

    # Start session while phone rings
    session_started = asyncio.create_task(
        session.start(
            agent=UKAgent(ctx, order_data),
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
    )

    # Dial the customer
    logger.info("Dialing %s via trunk %s", customer_phone, OUTBOUND_TRUNK_ID)
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=OUTBOUND_TRUNK_ID,
                sip_call_to=customer_phone,
                participant_identity=CALLEE_IDENTITY,
                participant_name=customer_name,
                wait_until_answered=True,
            )
        )
    except api.TwirpError as e:
        logger.error(
            "Call to %s failed: %s (sip_status=%s)",
            customer_phone,
            e.message,
            e.metadata.get("sip_status"),
        )

        # Mark as no_answer in DB
        update_delivery_confirmation(
            order_id=order_id,
            status=3,
            notes=f"Call failed: {e.message}",
        )

        session_started.cancel()
        ctx.shutdown()
        return

    await session_started

    # Build and speak the opening greeting
    items_summary = build_items_summary(order_data["items"])

    greeting = (
        f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। "
        f"कल आपके ऑर्डर की डिलीवरी है, इसलिए कॉल कर रही हूँ। "
        f"आपने {items_summary} ऑर्डर किया है, कुल ₹{int(order_data['total_amount'])} का। "
        f"डिलीवरी का पता {order_data['delivery_address']} है। "
        f"क्या कल {order_data['delivery_slot']} में कोई घर पर होगा?"
    )

    await session.say(greeting, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(server)
