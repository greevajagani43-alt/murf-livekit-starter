"""
trigger_server.py  —  Day 6: FastAPI HTTP endpoint to trigger outbound calls
─────────────────────────────────────────────────────────────────────────────
Start with:
    uv run uvicorn src.trigger_server:app --host 0.0.0.0 --port 8001 --reload

POST /call
    Body: { "phone_number": "+91XXXXXXXXXX", "customer_name": "Rahul", "reason": "restock" }
    Returns: { "room_name": "saathi_outbound_...", "participant_id": "..." }

GET /health
    Returns: { "status": "ok" }
"""

import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env.local")

from livekit import api as lkapi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Saathi Outbound Call Trigger",
    description="HTTP API to trigger outbound calls from Ratan Kirana Store's Saathi agent",
    version="1.0.0",
)


class CallRequest(BaseModel):
    phone_number: str  # E.164 format, e.g. +91XXXXXXXXXX
    customer_name: str = "Customer"
    reason: str = "restock"  # Used for logging / future analytics


class CallResponse(BaseModel):
    room_name: str
    participant_id: str
    message: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "saathi-outbound-trigger"}


@app.post("/call", response_model=CallResponse)
async def trigger_call(request: CallRequest):
    """
    Trigger an outbound call to a customer's phone number.
    The Saathi agent will automatically join the room and dial out.
    """
    livekit_url = os.environ.get("LIVEKIT_URL")
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    sip_trunk_id = os.environ.get("LIVEKIT_SIP_TRUNK_ID")

    if not all([livekit_url, api_key, api_secret, sip_trunk_id]):
        raise HTTPException(
            status_code=500,
            detail="Missing LiveKit or SIP Trunk configuration. Check .env.local",
        )

    safe_name = request.customer_name.replace(" ", "_").lower()
    room_name = f"saathi_outbound_{safe_name}_{uuid.uuid4().hex[:8]}"

    logger.info(
        "Outbound call → %s (%s)  room=%s  reason=%s",
        request.phone_number,
        request.customer_name,
        room_name,
        request.reason,
    )

    try:
        lk = lkapi.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        )

        # Create room
        await lk.room.create_room(lkapi.CreateRoomRequest(name=room_name))

        # Dial out via SIP
        sip_request = lkapi.CreateSIPParticipantRequest(
            sip_trunk_id=sip_trunk_id,
            sip_call_to=request.phone_number,
            room_name=room_name,
            participant_identity=f"phone_{request.phone_number.replace('+', '')}",
            participant_name=request.customer_name,
            krisp_enabled=True,
        )
        result = await lk.sip.create_sip_participant(sip_request)
        await lk.aclose()

        logger.info("SIP participant created: %s", result.participant_id)

        return CallResponse(
            room_name=room_name,
            participant_id=result.participant_id,
            message=f"Call initiated to {request.phone_number}. Agent is connecting.",
        )

    except Exception as exc:
        logger.error("Failed to trigger call: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
