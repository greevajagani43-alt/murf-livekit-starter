"""Trigger an outbound call for Ratan Kirana Store.

Usage examples:

    # Using SIP username (LiveKit appends the domain from trunk config)
    uv run python src/telephony/outbound/dial.py \
        --to kavan \
        --reason payment_reminder \
        --name "Rahul" \
        --metadata '{"amount": 450, "order_id": "ORD123"}'

    # Order confirmation
    uv run python src/telephony/outbound/dial.py \
        --to kavan \
        --reason order_confirmation \
        --name "Priya" \
        --metadata '{"items": "2x Aashirvaad Atta 5kg, 1x Amul Butter", "total": 650}'

    # Offer notification
    uv run python src/telephony/outbound/dial.py \
        --to kavan \
        --reason offer_notification \
        --name "Amit" \
        --metadata '{"offer": "Buy 2 Aashirvaad Atta, get ₹30 off"}'

Make sure the worker is running first:
    uv run python src/telephony/outbound/agent.py dev
"""

import argparse
import asyncio
import json
import uuid

from dotenv import load_dotenv
from livekit import api

load_dotenv(".env.local")

# Must match the agent_name in agent.py
AGENT_NAME = "outbound-agent"

VALID_REASONS = [
    "payment_reminder",
    "order_confirmation",
    "delivery_update",
    "offer_notification",
    "customer_callback",
    "delivery_confirmation",
]


def format_sip_address(address: str) -> str:
    """Format the SIP address for LiveKit's SipCallTo.
    
    LiveKit expects:
    - A phone number like '+15551234567' for PSTN calls
    - A SIP user like 'kavan' for SIP-to-SIP calls (NOT a full URI)
    
    The trunk config already knows the domain (sip.linphone.org),
    so just pass the username.
    """
    address = address.strip()
    
    # Remove 'sip:' prefix if present
    if address.startswith("sip:"):
        address = address[4:]
    
    # Remove @domain if present (trunk config handles the domain)
    if "@" in address:
        address = address.split("@")[0]
    
    # If it looks like a phone number (starts with +), return as-is
    if address.startswith("+"):
        return address
    
    # Return just the username
    return address


async def dial(
    sip_user: str,
    customer_name: str,
    reason: str,
    metadata: dict,
    room_name: str,
) -> None:
    """Create the room and dispatch the outbound agent into it."""
    lk = api.LiveKitAPI()
    try:
        await lk.room.create_room(api.CreateRoomRequest(name=room_name))

        # The agent reads this metadata to know who to call and why
        dispatch_metadata = json.dumps({
            "phone_number": sip_user,
            "customer_name": customer_name,
            "reason": reason,
            "metadata": metadata,
        })

        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
                metadata=dispatch_metadata,
            )
        )
    finally:
        await lk.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Place an outbound call from Ratan Kirana Store.",
        epilog="""
Examples:
  # Using SIP username (recommended for Linphone)
  %(prog)s --to kavan --name Rahul --reason payment_reminder --metadata '{"amount":450}'
  
  # Using phone number (for PSTN calls)
  %(prog)s --to +15551234567 --name Priya --reason order_confirmation
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--to",
        required=True,
        help="SIP username (e.g., kavan) or phone number (e.g., +15551234567). "
             "Do NOT pass full SIP URI like sip:user@domain — the trunk config handles the domain.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Customer name to greet",
    )
    parser.add_argument(
        "--reason",
        required=True,
        choices=VALID_REASONS,
        help="Reason for the outbound call",
    )
    parser.add_argument(
        "--metadata",
        default="{}",
        help="Additional context as JSON string (e.g., '{\"amount\": 450}')",
    )
    parser.add_argument(
        "--room",
        default=None,
        help="Room name to use. Defaults to a generated one.",
    )
    args = parser.parse_args()

    # Format the SIP address — strip sip: prefix and @domain
    formatted_number = format_sip_address(args.to)

    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError:
        print(f"Error: --metadata must be valid JSON. Got: {args.metadata}")
        return

    room_name = args.room or f"outbound-{uuid.uuid4().hex[:8]}"

    print(f"📞 Placing {args.reason} call...")
    print(f"   To: {formatted_number}")
    print(f"   Customer: {args.name}")
    print(f"   Room: {room_name}")
    if metadata:
        print(f"   Context: {json.dumps(metadata, indent=2)}")

    asyncio.run(dial(formatted_number, args.name, args.reason, metadata, room_name))

    print(f"\n✅ Dispatched {AGENT_NAME} to room '{room_name}'")
    print("Watch the worker terminal for call progress.")


if __name__ == "__main__":
    main()