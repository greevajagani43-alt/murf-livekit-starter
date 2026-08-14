"""
trigger_delivery_calls.py
─────────────────────────
Script to trigger UK delivery confirmation calls for all orders
scheduled for delivery tomorrow.

Usage:
    uv run python src/telephony/outbound/trigger_delivery_calls.py
    
    # Dry run — just show what would be called
    uv run python src/telephony/outbound/trigger_delivery_calls.py --dry-run
    
    # Call for a specific order
    uv run python src/telephony/outbound/trigger_delivery_calls.py --order-id ORD-20260811-001

Make sure the UK agent worker is running first:
    uv run python src/telephony/outbound/uk_agent.py dev
"""

import argparse
import asyncio
import json
import os
import sys
import uuid

from dotenv import load_dotenv
from livekit import api

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database_orders import init_orders_db, seed_orders_if_empty, get_orders_delivering_tomorrow, get_order_by_id

load_dotenv(".env.local")

AGENT_NAME = "uk-agent"


async def trigger_call_for_order(order: dict) -> None:
    """Create a room and dispatch the UK agent for one order."""
    lk = api.LiveKitAPI()
    room_name = f"uk-delivery-{order['order_id'].lower()}-{uuid.uuid4().hex[:6]}"
    
    try:
        await lk.room.create_room(api.CreateRoomRequest(name=room_name))
        
        dispatch_metadata = json.dumps({
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "customer_phone": order["customer_phone"],
        })
        
        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
                metadata=dispatch_metadata,
            )
        )
        
        print(f"  ✅ Dispatched to room: {room_name}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    finally:
        await lk.aclose()


async def main():
    parser = argparse.ArgumentParser(
        description="Trigger UK delivery confirmation calls for tomorrow's orders."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be called without actually calling",
    )
    parser.add_argument(
        "--order-id",
        type=str,
        help="Call for a specific order ID instead of all tomorrow's orders",
    )
    args = parser.parse_args()
    
    # Initialize DB
    init_orders_db()
    seed_orders_if_empty()
    
    if args.order_id:
        # Single order mode
        print(f"\n📦 Looking up order: {args.order_id}")
        order = get_order_by_id(args.order_id)
        
        if not order:
            print(f"❌ Order not found: {args.order_id}")
            return
        
        orders = [order]
    else:
        # All tomorrow's deliveries
        print("\n🔍 Finding orders delivering tomorrow…")
        orders = get_orders_delivering_tomorrow()
    
    if not orders:
        print("📭 No orders found for delivery tomorrow.")
        return
    
    print(f"\n📋 Found {len(orders)} order(s) for delivery confirmation:\n")
    
    for order in orders:
        items_summary = ", ".join(
            f"{item['qty']}x {item['product_name']}" 
            for item in order["items"]
        )
        print(f"  Order: {order['order_id']}")
        print(f"  Customer: {order['customer_name']}")
        print(f"  Phone: {order['customer_phone']}")
        print(f"  Items: {items_summary}")
        print(f"  Address: {order['delivery_address']}")
        print(f"  Slot: {order['delivery_slot']}")
        print(f"  Total: ₹{int(order['total_amount'])}")
        print()
    
    if args.dry_run:
        print("🏃 Dry run — no calls placed.")
        print("Run without --dry-run to actually place calls.")
        return
    
    print(f"📞 Placing {len(orders)} confirmation call(s)…\n")
    
    for order in orders:
        print(f"📞 Calling {order['customer_name']} for order {order['order_id']}…")
        await trigger_call_for_order(order)
        # Small delay between calls
        await asyncio.sleep(2)
    
    print("\n✅ All calls dispatched!")
    print("Watch the UK agent worker terminal for call progress.")


if __name__ == "__main__":
    asyncio.run(main())