"""
database_orders.py
──────────────────
Order management for Ratan Kirana & General Store.

Handles:
- Creating orders when placed via voice calls
- Looking up orders by ID
- Finding orders that need delivery confirmation calls (delivering tomorrow)
- Updating delivery confirmation status

Database: data/orders.db (SQLite)
"""

import json
import logging
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

logger = logging.getLogger("database_orders")

# DB path — data/orders.db relative to backend/
_DB_PATH = Path(__file__).parent.parent / "data" / "orders.db"

# Schema path for initialization
_SCHEMA_PATH = Path(__file__).parent.parent / "data" / "schema_orders.sql"


def _get_conn() -> sqlite3.Connection:
    """Get a connection to the orders database."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    # conn.execute("PRAGMA foreign_keys = ON")  # Disabled: users table is in a different DB
    return conn


def init_orders_db() -> None:
    """Initialize the orders database with schema if it doesn't exist."""
    try:
        with _get_conn() as conn:
            # Check if table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
            )
            if cursor.fetchone() is None:
                logger.info("Initializing orders database…")
                if _SCHEMA_PATH.exists():
                    with open(_SCHEMA_PATH, "r") as f:
                        conn.executescript(f.read())
                    logger.info("Orders database initialized successfully")
                else:
                    logger.error(f"Schema file not found: {_SCHEMA_PATH}")
            else:
                logger.info("Orders database already exists")
    except Exception as e:
        logger.error(f"Failed to initialize orders database: {e}")
        raise


def create_order(
    order_id: str,
    user_id: str,
    customer_name: str,
    customer_phone: str,
    delivery_address: str,
    delivery_date: str,
    items: List[Dict[str, Any]],
    total_amount: float,
    delivery_slot: str = "morning",
    payment_method: str = "cod",
    payment_status: str = "pending",
) -> bool:
    """Create a new order in the database."""

    # Check database exists before creating the order
    if not _DB_PATH.exists():
        logger.error(f"Orders database not found: {_DB_PATH}")
        return False

    try:
        with _get_conn() as conn:
            items_json = json.dumps(items, ensure_ascii=False)
            now = datetime.utcnow().isoformat()

            conn.execute(
                """INSERT INTO orders 
                   (order_id, user_id, customer_name, customer_phone, 
                    delivery_address, delivery_date, delivery_slot,
                    items, total_amount, status, payment_status, 
                    payment_method, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    order_id,
                    user_id,
                    customer_name,
                    customer_phone,
                    delivery_address,
                    delivery_date,
                    delivery_slot,
                    items_json,
                    total_amount,
                    "confirmed",
                    payment_status,
                    payment_method,
                    now,
                    now,
                ),
            )

            logger.info(f"Order created: {order_id} for {customer_name}")
            return True

    except Exception as e:
        logger.error(f"Failed to create order {order_id}: {e}")
        return False


def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    """Look up an order by its ID.

    Args:
        order_id: The order ID to look up

    Returns:
        Order dict with items parsed as list, or None if not found
    """
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE order_id = ?", (order_id,)
            ).fetchone()

            if row is None:
                logger.warning(f"Order not found: {order_id}")
                return None

            order = dict(row)
            # Parse items JSON back to list
            order["items"] = json.loads(order["items"])
            return order
    except Exception as e:
        logger.error(f"Error looking up order {order_id}: {e}")
        return None


def get_orders_delivering_tomorrow() -> List[Dict[str, Any]]:
    """Find all orders that are delivering tomorrow and haven't been confirmed yet.

    Used by the UK agent to know which customers to call.

    Returns:
        List of order dicts with items parsed
    """
    try:
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        with _get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM orders 
                   WHERE delivery_date = ? 
                   AND status = 'confirmed'
                   AND delivery_confirmed = 0
                   ORDER BY delivery_slot""",
                (tomorrow,),
            ).fetchall()

            orders = []
            for row in rows:
                order = dict(row)
                order["items"] = json.loads(order["items"])
                orders.append(order)

            logger.info(f"Found {len(orders)} orders delivering tomorrow")
            return orders
    except Exception as e:
        logger.error(f"Error finding tomorrow's deliveries: {e}")
        return []


def get_orders_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Get all orders for a specific user, most recent first.

    Args:
        user_id: The customer's user_id

    Returns:
        List of order dicts
    """
    try:
        with _get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM orders 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC""",
                (user_id,),
            ).fetchall()

            orders = []
            for row in rows:
                order = dict(row)
                order["items"] = json.loads(order["items"])
                orders.append(order)

            return orders
    except Exception as e:
        logger.error(f"Error getting orders for user {user_id}: {e}")
        return []


def update_delivery_confirmation(
    order_id: str,
    status: int,
    notes: Optional[str] = None,
) -> bool:
    """Update the delivery confirmation status after calling the customer.

    Args:
        order_id: The order ID
        status: 0=not called, 1=confirmed, 2=rescheduled, 3=no_answer
        notes: Optional notes from the call (e.g., "Customer will be home after 10 AM")

    Returns:
        True if updated successfully
    """
    try:
        with _get_conn() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """UPDATE orders 
                   SET delivery_confirmed = ?,
                       delivery_confirmation_notes = ?,
                       updated_at = ?
                   WHERE order_id = ?""",
                (status, notes, now, order_id),
            )
            logger.info(
                f"Updated delivery confirmation for {order_id}: status={status}"
            )
            return True
    except Exception as e:
        logger.error(f"Failed to update confirmation for {order_id}: {e}")
        return False


def update_order_status(order_id: str, status: str) -> bool:
    """Update the order status (confirmed, out_for_delivery, delivered, cancelled).

    Args:
        order_id: The order ID
        status: New status

    Returns:
        True if updated
    """
    try:
        with _get_conn() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """UPDATE orders 
                   SET status = ?, updated_at = ?
                   WHERE order_id = ?""",
                (status, now, order_id),
            )
            logger.info(f"Order {order_id} status updated to {status}")
            return True
    except Exception as e:
        logger.error(f"Failed to update status for {order_id}: {e}")
        return False


# ── Seed data for testing ──────────────────────────────────────────────────

SEED_ORDERS = [
    {
        "order_id": "ORD-20260811-001",
        "user_id": "user_1786292336644_1r72hdehokn",
        "customer_name": "Kavan",
        "customer_phone": "sip:kavan",
        "delivery_address": "42 Shivaji Nagar, Maninagar, Ahmedabad",
        "delivery_date": (date.today() + timedelta(days=1)).isoformat(),  # Tomorrow
        "delivery_slot": "morning",
        "items": [
            {"product_name": "Aashirvaad Atta 5 kg", "qty": 2, "price": 295},
            {"product_name": "Amul Butter 100 g", "qty": 1, "price": 60},
        ],
        "total_amount": 650.0,
        "payment_method": "cod",
        "payment_status": "pending",
    },
    {
        "order_id": "ORD-20260811-002",
        "user_id": "user_1786292336644_1r72hdehokn",
        "customer_name": "Kavan",
        "customer_phone": "sip:kavan",
        "delivery_address": "42 Shivaji Nagar, Maninagar, Ahmedabad",
        "delivery_date": (date.today() + timedelta(days=1)).isoformat(),  # Tomorrow
        "delivery_slot": "evening",
        "items": [
            {"product_name": "Tata Tea Premium 500 g", "qty": 1, "price": 280},
            {"product_name": "Parle-G Biscuits 800 g", "qty": 2, "price": 100},
            {"product_name": "Madhur Sugar 1 kg", "qty": 1, "price": 48},
        ],
        "total_amount": 528.0,
        "payment_method": "gpay",
        "payment_status": "pending",
    },
]


def seed_orders_if_empty() -> None:
    """Seed the orders table with test data if it's empty."""
    try:
        with _get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            if count == 0:
                logger.info(
                    "Seeding orders table with %d test orders…", len(SEED_ORDERS)
                )
                now = datetime.utcnow().isoformat()
                for order in SEED_ORDERS:
                    conn.execute(
                        """INSERT INTO orders 
                           (order_id, user_id, customer_name, customer_phone,
                            delivery_address, delivery_date, delivery_slot,
                            items, total_amount, status, payment_status,
                            payment_method, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            order["order_id"],
                            order["user_id"],
                            order["customer_name"],
                            order["customer_phone"],
                            order["delivery_address"],
                            order["delivery_date"],
                            order["delivery_slot"],
                            json.dumps(order["items"], ensure_ascii=False),
                            order["total_amount"],
                            "confirmed",
                            order["payment_status"],
                            order["payment_method"],
                            now,
                            now,
                        ),
                    )
                logger.info("Seed complete")
            else:
                logger.info("Orders table already has %d rows — skipping seed", count)
    except Exception as e:
        logger.error(f"Failed to seed orders: {e}")
