"""
telephony/outbound/dial.py — Trigger outbound call via LiveKit SIP API
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

load_dotenv(src_dir.parent / ".env.local")

from livekit import api as lkapi

logger = logging.getLogger("dial")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)


async def make_outbound_call(
    to: str,
    name: str = "Customer",
    reason: str | None = None,
    metadata: str | dict | None = None,
    trunk_id: str | None = None,
    dry_run: bool = False,
) -> None:
    livekit_url = os.environ.get("LIVEKIT_URL", "")
    api_key = os.environ.get("LIVEKIT_API_KEY", "")
    api_secret = os.environ.get("LIVEKIT_API_SECRET", "")
    sip_trunk_id = trunk_id or os.environ.get("LIVEKIT_SIP_TRUNK_ID", "")

    if not livekit_url or not api_key or not api_secret:
        logger.error("LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set in .env.local")
        raise SystemExit(1)

    if not sip_trunk_id:
        logger.error("LIVEKIT_SIP_TRUNK_ID is not set. Set it in .env.local or pass --trunk-id.")
        raise SystemExit(1)

    safe_name = name.replace(" ", "_").lower()
    room_name = f"saathi_outbound_{safe_name}_{uuid.uuid4().hex[:8]}"

    parsed_metadata = {}
    if isinstance(metadata, str):
        try:
            parsed_metadata = json.loads(metadata)
        except Exception:
            parsed_metadata = {"raw": metadata}
    elif isinstance(metadata, dict):
        parsed_metadata = metadata

    if reason:
        parsed_metadata["reason"] = reason

    logger.info("─" * 60)
    logger.info("Outbound call configuration:")
    logger.info("  To (Target SIP/Phone): %s", to)
    logger.info("  Name                 : %s", name)
    logger.info("  Reason               : %s", reason)
    logger.info("  Metadata             : %s", json.dumps(parsed_metadata))
    logger.info("  Room                 : %s", room_name)
    logger.info("  SIP Trunk ID         : %s", sip_trunk_id)
    logger.info("  LiveKit URL          : %s", livekit_url)
    logger.info("─" * 60)

    if dry_run:
        logger.info("DRY RUN — call not dispatched.")
        return

    lk = lkapi.LiveKitAPI(
        url=livekit_url,
        api_key=api_key,
        api_secret=api_secret,
    )

    logger.info("Creating LiveKit room: %s", room_name)
    await lk.room.create_room(
        lkapi.CreateRoomRequest(
            name=room_name,
            metadata=json.dumps(parsed_metadata) if parsed_metadata else "",
        )
    )

    try:
        logger.info("Dispatching agent 'my-agent' to room %s …", room_name)
        dispatch = await lk.agent_dispatch.create_dispatch(
            lkapi.CreateAgentDispatchRequest(
                agent_name="my-agent",
                room=room_name,
                metadata=json.dumps(parsed_metadata) if parsed_metadata else "",
            )
        )
        logger.info("Agent dispatched: %s", dispatch.id)
    except Exception as e:
        logger.warning("Agent dispatch notice: %s", e)

    clean_identity = to.replace("+", "").replace("@", "_").replace(".", "_")
    logger.info("Dialling %s via SIP trunk %s …", to, sip_trunk_id)
    sip_request = lkapi.CreateSIPParticipantRequest(
        sip_trunk_id=sip_trunk_id,
        sip_call_to=to,
        room_name=room_name,
        participant_identity=f"sip_{clean_identity}",
        participant_name=name,
        krisp_enabled=True,
    )
    result = await lk.sip.create_sip_participant(sip_request)

    logger.info("SIP participant created successfully: %s", result.participant_id)
    logger.info("Call is ringing... Agent will handle conversation automatically.")

    await lk.aclose()


def main():
    parser = argparse.ArgumentParser(description="Call maker CLI for LiveKit outbound SIP")
    parser.add_argument("--to", "--number", required=True, help="SIP Extension/URI or Phone Number (e.g. si0nk345 or +91...)")
    parser.add_argument("--name", default="Customer", help="Customer name")
    parser.add_argument("--reason", default=None, help="Call reason")
    parser.add_argument("--metadata", default=None, help="JSON metadata string")
    parser.add_argument("--trunk-id", default=None, help="SIP trunk ID override")
    parser.add_argument("--dry-run", action="store_true", help="Print config without calling")

    args, unknown = parser.parse_known_args()

    metadata_str = args.metadata
    if unknown:
        if metadata_str:
            metadata_str = metadata_str + " " + " ".join(unknown)
        else:
            metadata_str = " ".join(unknown)

    if metadata_str:
        metadata_str = metadata_str.replace('\\"', '"')

    asyncio.run(
        make_outbound_call(
            to=args.to,
            name=args.name,
            reason=args.reason,
            metadata=metadata_str,
            trunk_id=args.trunk_id,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
