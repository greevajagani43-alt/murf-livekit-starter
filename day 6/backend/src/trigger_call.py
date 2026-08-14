"""
trigger_call.py  —  Day 6: Fire an outbound call from the CLI
──────────────────────────────────────────────────────────────
This script:
  1. Creates a new LiveKit room (or uses an existing one)
  2. Creates a SIP Participant (outbound dial) via LiveKit SIP API
     → LiveKit calls out to your Twilio SIP Trunk
     → Twilio dials the customer's PSTN number
  3. The agent (agent.py) picks up the room and connects to the call

Usage:
  uv run python src/trigger_call.py --number +91XXXXXXXXXX
  uv run python src/trigger_call.py --number +91XXXXXXXXXX --name "Rahul Sharma" --dry-run

Environment variables required (in backend/.env.local):
  LIVEKIT_URL            wss://your-project.livekit.cloud
  LIVEKIT_API_KEY        your key
  LIVEKIT_API_SECRET     your secret
  LIVEKIT_SIP_TRUNK_ID   your outbound SIP trunk ID (from LiveKit console)
"""

import argparse
import asyncio
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env.local")

# LiveKit Server SDK
from livekit import api as lkapi

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)


async def trigger_outbound_call(
    phone_number: str,
    customer_name: str = "Customer",
    trunk_id: str | None = None,
    dry_run: bool = False,
) -> None:
    """
    Dispatch an outbound SIP call to `phone_number` via LiveKit + Twilio.

    Args:
        phone_number:   E.164 format, e.g. +91XXXXXXXXXX
        customer_name:  Friendly name shown in LiveKit console
        trunk_id:       LiveKit SIP Trunk ID (overrides env var)
        dry_run:        If True, print config but don't actually call
    """
    livekit_url = os.environ["LIVEKIT_URL"]
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]
    sip_trunk_id = trunk_id or os.environ.get("LIVEKIT_SIP_TRUNK_ID", "")

    if not sip_trunk_id:
        logger.error(
            "LIVEKIT_SIP_TRUNK_ID is not set. "
            "Create an outbound SIP trunk in the LiveKit console and set this env var."
        )
        raise SystemExit(1)

    # Generate a unique room name so each call gets its own room
    safe_name = customer_name.replace(" ", "_").lower()
    room_name = f"saathi_outbound_{safe_name}_{uuid.uuid4().hex[:8]}"

    logger.info("─" * 60)
    logger.info("Outbound call configuration:")
    logger.info("  Phone number  : %s", phone_number)
    logger.info("  Customer name : %s", customer_name)
    logger.info("  Room          : %s", room_name)
    logger.info("  SIP Trunk ID  : %s", sip_trunk_id)
    logger.info("  LiveKit URL   : %s", livekit_url)
    logger.info("─" * 60)

    if dry_run:
        logger.info("DRY RUN — no call placed.")
        return

    # Build LiveKit client
    lk = lkapi.LiveKitAPI(
        url=livekit_url,
        api_key=api_key,
        api_secret=api_secret,
    )

    # Create the room first so the agent can join immediately
    logger.info("Creating LiveKit room: %s", room_name)
    await lk.room.create_room(
        lkapi.CreateRoomRequest(name=room_name)
    )

    # Create outbound SIP participant — this dials the phone
    logger.info("Dialling %s via SIP trunk %s …", phone_number, sip_trunk_id)
    sip_request = lkapi.CreateSIPParticipantRequest(
        sip_trunk_id=sip_trunk_id,
        sip_call_to=phone_number,
        room_name=room_name,
        participant_identity=f"phone_{phone_number.replace('+', '')}",
        participant_name=customer_name,
        # Optional: caller-ID display name sent to Twilio
        krisp_enabled=True,  # Krisp noise suppression on the SIP leg
    )
    result = await lk.sip.create_sip_participant(sip_request)

    logger.info("SIP participant created: %s", result.participant_id)
    logger.info("Call is ringing… the agent will join automatically.")
    logger.info("Watch the LiveKit console for room activity.")

    await lk.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trigger an outbound call from Saathi (Ratan Kirana Store)"
    )
    parser.add_argument(
        "--number",
        required=True,
        help="Customer phone number in E.164 format, e.g. +91XXXXXXXXXX",
    )
    parser.add_argument(
        "--name",
        default="Customer",
        help="Customer's name (used for room naming and greeting)",
    )
    parser.add_argument(
        "--trunk-id",
        default=None,
        help="LiveKit SIP Trunk ID (overrides LIVEKIT_SIP_TRUNK_ID env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print config only — don't actually place the call",
    )
    args = parser.parse_args()

    asyncio.run(
        trigger_outbound_call(
            phone_number=args.number,
            customer_name=args.name,
            trunk_id=args.trunk_id,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
