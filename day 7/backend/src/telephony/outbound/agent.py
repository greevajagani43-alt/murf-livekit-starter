"""Outbound telephony agent — places calls for Ratan Kirana Store.

Handles payment reminders, order confirmations, delivery updates,
offer notifications, and customer callbacks.

Run the worker with:
    uv run python src/telephony/outbound/agent.py dev

Then trigger a call from another terminal:
    uv run python src/telephony/outbound/dial.py --to sip:kavan --reason payment_reminder --name "Rahul" --metadata '{"amount": 450, "order_id": "ORD123"}'
"""

import asyncio
import json
import logging
import os

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

# Import your existing tools and DB helpers
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools import lookup_user, save_user_profile, lookup_catalogue, check_stock

logger = logging.getLogger("outbound-agent")

load_dotenv(".env.local")

# Your existing Linphone trunk ID from LiveKit dashboard
OUTBOUND_TRUNK_ID = os.getenv("LIVEKIT_SIP_OUTBOUND_TRUNK_ID")

# Optional — a phone number to transfer people to when they ask for a human.
TRANSFER_TO_NUMBER = os.getenv("TRANSFER_TO_NUMBER", "098250-XXXXX")

# The identity LiveKit gives the person we call.
CALLEE_IDENTITY = "phone-user"

# ── Outbound System Prompt ─────────────────────────────────────────────────

OUTBOUND_SYSTEM_PROMPT = """
IDENTITY

You are Saathi, the voice assistant for Ratan Kirana & General Store in Ahmedabad.
You are making an OUTBOUND call to a customer named {customer_name}.
The reason for this call is: {reason}.

STORE INFORMATION
Name: Ratan Kirana & General Store
Location: Maninagar, Ahmedabad
Timings: 8 AM to 10 PM every day
Payment: Cash on delivery, GPay, PhonePe, Paytm.
Contact: 098250-XXXXX

CALL REASON: {reason}

---
payment_reminder:
You are calling to remind the customer about a pending payment.
Additional context: {metadata}

1. Greet the customer warmly by name.
2. Inform them about the pending payment politely.
3. State the amount and order reference clearly.
4. Ask if they can make the payment now or need more time.
5. Remind them of payment options: Cash on delivery, GPay, PhonePe, Paytm.
6. Never ask for OTP, PIN, or card details.
7. If they say they'll pay, thank them and confirm.
8. If they have questions, answer helpfully.

Example opening in Hindi:
"नमस्ते [Name] जी! मैं रतन किराना स्टोर से साथी बोल रहा हूँ। आपके ऑर्डर का [amount] रुपये का पेमेंट बाकी है। क्या आप आज पेमेंट कर पाएँगे?"

Example opening in English:
"Hello [Name]! This is Saathi calling from Ratan Kirana Store. There's a pending payment of ₹[amount] for your order. Would you be able to make the payment today?"

---
order_confirmation:
You are calling to confirm an order before delivery.
Additional context: {metadata}

1. Greet the customer warmly.
2. Summarize their order (items, quantities, total).
3. Confirm the delivery address.
4. Ask if everything is correct.
5. Confirm the expected delivery time.
6. Thank them for their order.

---
delivery_update:
You are calling to update the customer about their delivery status.
Additional context: {metadata}

1. Greet the customer warmly.
2. Tell them their order is on the way / delayed / delivered.
3. Provide the estimated delivery time if available.
4. Ask if they have any questions.

---
offer_notification:
You are calling to inform the customer about a special offer.
Additional context: {metadata}

1. Greet the customer warmly.
2. Mention the offer naturally.
3. Ask if they're interested.
4. If yes, help them place an order using the standard order flow.
5. Use lookup_catalogue and check_stock tools as needed.

---
customer_callback:
You are returning a customer's callback request.
Additional context: {metadata}

1. Greet the customer warmly.
2. Mention that you're returning their call.
3. Ask how you can help them today.
4. Proceed with standard order flow if they want to order.
5. Use lookup_catalogue and check_stock tools as needed.

---

GENERAL OUTBOUND GUIDELINES

1. Always greet the customer by name.
2. Identify yourself as Saathi from Ratan Kirana Store.
3. State the purpose of the call clearly but politely.
4. If the customer doesn't answer or the line is busy:
   - Wait for voicemail if available
   - Leave a brief message with the store name and callback number
5. If the customer says it's a bad time:
   - Apologize briefly
   - Ask when would be a good time to call back
   - Note the preferred time
6. Never be pushy or aggressive.
7. Always be polite and helpful.

LANGUAGE & SCRIPT

CRITICAL: Always match the customer's language. If they speak in English, respond in English. If they speak in Hindi, respond in Hindi.
Always write every language in its own native script.
Hindi → Devanagari (नमस्ते), never romanized (never "namaste").
English → Latin script (Hello).

STYLE
Use short sentences.
Keep each sentence under 20 words whenever possible.
Speak naturally like a neighbourhood shop assistant.
Be warm and friendly but professional.
Do not use bullet points, lists, markdown, or technical language.

GUARDRAILS
Never ask for OTP, PIN, bank account number, card details, or payment credentials.
Never give medical, legal, or financial advice.
If the customer is rude, remain calm and professional.

CALL END
End the call with a warm goodbye.
Example in Hindi: "धन्यवाद! रतन किराना स्टोर से आपका दिन शुभ हो!"
Example in English: "Thank you! Have a great day from Ratan Kirana Store!"
"""


def build_greeting(customer_name: str, reason: str, metadata: dict) -> str:
    """Build the opening greeting based on the call reason."""
    
    greetings = {
        "payment_reminder": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। आपके ऑर्डर का {metadata.get('amount', '___')} रुपये का पेमेंट बाकी है। क्या आप आज पेमेंट कर पाएँगे?",
            "en": f"Hello {customer_name}! This is Saathi calling from Ratan Kirana Store. There's a pending payment of ₹{metadata.get('amount', '___')} for your order. Would you be able to make the payment today?",
        },
        "order_confirmation": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। मैं आपके ऑर्डर की पुष्टि करने के लिए कॉल कर रही हूँ। क्या आपके पास एक मिनट है?",
            "en": f"Hello {customer_name}! This is Saathi from Ratan Kirana Store. I'm calling to confirm your order. Do you have a moment?",
        },
        "delivery_update": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। आपके ऑर्डर के बारे में अपडेट है।",
            "en": f"Hello {customer_name}! This is Saathi from Ratan Kirana Store. I have an update about your delivery.",
        },
        "offer_notification": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। आज आपके लिए एक खास ऑफर है!",
            "en": f"Hello {customer_name}! This is Saathi from Ratan Kirana Store. I have a special offer for you today!",
        },
        "customer_callback": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। आपने हमें कॉल करने के लिए कहा था। मैं आपकी क्या मदद कर सकती हूँ?",
            "en": f"Hello {customer_name}! This is Saathi from Ratan Kirana Store. You had requested a callback. How can I help you today?",
        },
        "delivery_confirmation": {
            "hi": f"नमस्ते {customer_name} जी! मैं रतन किराना स्टोर से साथी बोल रही हूँ। कल आपके ऑर्डर की डिलीवरी है, क्या आप घर पर होंगे?",
            "en": f"Hello {customer_name}! This is Saathi from Ratan Kirana Store. Your order is scheduled for delivery tomorrow. Will you be home?",
        },
    }
    
    # Default to Hindi for Indian store
    return greetings.get(reason, greetings["customer_callback"]).get("hi", greetings["customer_callback"]["en"])


class OutboundAgent(Agent):
    """Saathi outbound calling agent for Ratan Kirana Store."""

    def __init__(self, ctx: JobContext, customer_name: str, reason: str, metadata: dict) -> None:
        instructions = OUTBOUND_SYSTEM_PROMPT.format(
            customer_name=customer_name,
            reason=reason,
            metadata=json.dumps(metadata, indent=2),
        )
        super().__init__(
            instructions=instructions,
            tools=[lookup_user, save_user_profile, lookup_catalogue, check_stock],
        )
        self.ctx = ctx
        self.customer_name = customer_name
        self.reason = reason
        self.metadata = metadata

    @function_tool
    async def transfer_to_human(self, context: RunContext) -> str:
        """Transfer the person to a human at the store.

        Use this when they explicitly ask for a person, or when you cannot help
        them with their request.
        """
        if not TRANSFER_TO_NUMBER:
            return "Transfers are not available on this line. Offer to have someone call back instead."

        await context.session.generate_reply(
            instructions="Tell them you're connecting them to the store owner now."
        )

        logger.info("transferring call to %s", TRANSFER_TO_NUMBER)
        try:
            await self.ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=self.ctx.room.name,
                    participant_identity=CALLEE_IDENTITY,
                    transfer_to=f"tel:{TRANSFER_TO_NUMBER}",
                    play_dialtone=True,
                )
            )
        except Exception:
            logger.exception("transfer failed")
            return "The transfer did not go through. Apologize and offer a call back."

        return "Transferred."

    @function_tool
    async def detected_answering_machine(self, context: RunContext) -> str:
        """Hang up because the call reached a voicemail or answering machine.

        Use this as soon as you hear a recorded greeting rather than a live person.
        """
        logger.info("answering machine detected — hanging up")
        await self._hangup()
        return "Call ended."

    @function_tool
    async def end_call(self, context: RunContext) -> str:
        """Hang up the call.

        Use this once the conversation is finished and you have said goodbye.
        """
        await context.session.generate_reply(
            instructions="Thank them for their time and say a short goodbye. If speaking Hindi, say 'धन्यवाद! रतन किराना स्टोर से आपका दिन शुभ हो!' If English, say 'Thank you! Have a great day from Ratan Kirana Store!'"
        )

        logger.info("ending call")
        await self._hangup()
        return "Call ended."

    async def _hangup(self) -> None:
        """Delete the room, which drops the SIP leg and ends the phone call."""
        await self.ctx.api.room.delete_room(
            api.DeleteRoomRequest(room=self.ctx.room.name)
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


def parse_metadata(ctx: JobContext) -> dict:
    """Parse dispatch metadata into a structured dict."""
    metadata = ctx.job.metadata
    if not metadata:
        return {}
    try:
        return json.loads(metadata)
    except json.JSONDecodeError:
        return {"raw": metadata.strip()}


@server.rtc_session(agent_name="outbound-agent")
async def outbound_agent(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    metadata = parse_metadata(ctx)
    
    phone_number = metadata.get("phone_number")
    customer_name = metadata.get("customer_name", "Customer")
    reason = metadata.get("reason", "customer_callback")
    call_metadata = metadata.get("metadata", {})

    if not phone_number:
        logger.error(
            "no phone_number in metadata — dispatch with "
            '{"phone_number": "sip:kavan", "customer_name": "Rahul", "reason": "payment_reminder"}'
        )
        ctx.shutdown()
        return

    if not OUTBOUND_TRUNK_ID:
        logger.error("LIVEKIT_SIP_OUTBOUND_TRUNK_ID is not set — cannot place calls")
        ctx.shutdown()
        return

    logger.info(
        "Outbound call to %s — customer=%s reason=%s metadata=%s",
        phone_number, customer_name, reason, call_metadata,
    )

    await ctx.connect()

    # Same voice pipeline as your main agent
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-3.5-flash-lite"),
        tts=murf.TTS(
            voice="Anisha",  # Hindi-capable voice
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Start the session while the phone is still ringing
    session_started = asyncio.create_task(
        session.start(
            agent=OutboundAgent(ctx, customer_name, reason, call_metadata),
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

    logger.info("dialing %s via trunk %s", phone_number, OUTBOUND_TRUNK_ID)
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=OUTBOUND_TRUNK_ID,
                sip_call_to=phone_number,
                participant_identity=CALLEE_IDENTITY,
                participant_name=customer_name,
                wait_until_answered=True,
            )
        )
    except api.TwirpError as e:
        logger.error(
            "call to %s failed: %s (sip_status=%s)",
            phone_number,
            e.message,
            e.metadata.get("sip_status"),
        )
        session_started.cancel()
        ctx.shutdown()
        return

    await session_started

    # Build and speak the opening greeting
    greeting = build_greeting(customer_name, reason, call_metadata)
    await session.say(greeting, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(server)