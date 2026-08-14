"""
tools.py
────────
Function tools for the Saathi voice agent.
Extracted from agent.py so the main file stays focused on session plumbing.

Exports:
    make_tools(user_id: str) → list of bound @function_tool instances

Each tool is a standalone async function decorated with @function_tool.
Import and attach them to the Assistant class in agent.py.
"""

import logging
from typing import Optional

from livekit.agents import RunContext, function_tool

from database import get_user, save_user
from database_products import search_products, get_products_by_category, get_product_stock

logger = logging.getLogger("tools")


# ── User memory tools ─────────────────────────────────────────────────────


@function_tool
async def lookup_user(context: RunContext, user_id: str) -> Optional[str]:
    """Look up a returning customer's profile and facts.

    Use this at the START of every call to check if you already know this customer.
    Returns their name, past orders, usual quantity, and delivery preferences.
    Returns None if the customer is new.

    Args:
        user_id: The unique customer identifier (from the call session)
    """
    logger.info("Looking up customer: %s", user_id)
    user_data = get_user(user_id)

    if user_data is None:
        logger.info("New customer: %s", user_id)
        return None

    name = user_data["name"]
    facts = user_data["facts"]
    logger.info("Returning customer: %s — facts: %s", name, facts)

    summary = f"Name: {name}. "
    if facts.get("delivery_address"):
        summary += f"Saved delivery address: {facts['delivery_address']}. "
    if facts.get("usual_quantity"):
        summary += f"Usually orders: {facts['usual_quantity']}. "
    if facts.get("preferred_slot"):
        summary += f"Prefers delivery: {facts['preferred_slot']}. "
    if facts.get("past_orders"):
        past = facts["past_orders"]
        if isinstance(past, list) and past:
            summary += f"Previous orders: {', '.join(past[-3:])}."

    return summary


@function_tool
async def save_user_profile(
    context: RunContext,
    user_id: str,
    name: str,
    delivery_address: Optional[str] = None,
    usual_quantity: Optional[str] = None,
    preferred_slot: Optional[str] = None,
    past_orders: Optional[list] = None,
) -> str:
    """Save or update a customer's profile and facts (ONLY after getting verbal consent).

    CRITICAL: ONLY call this AFTER the customer has clearly said YES to saving their data.
    Never save without explicit permission.

    Args:
        user_id: The unique customer identifier
        name: Customer's name
        delivery_address: Their delivery address (e.g., "42 Shivaji Nagar, Maninagar")
        usual_quantity: What they usually order (e.g., "2 Aashirvaad Atta 5kg")
        preferred_slot: When they prefer delivery (e.g., "morning", "evening")
        past_orders: List of recent order summaries
    """
    logger.info("Saving customer profile: %s (%s)", name, user_id)

    facts: dict = {}
    if delivery_address:
        facts["delivery_address"] = delivery_address
    if usual_quantity:
        facts["usual_quantity"] = usual_quantity
    if preferred_slot:
        facts["preferred_slot"] = preferred_slot
    if past_orders:
        facts["past_orders"] = past_orders

    success = save_user(user_id, name, facts)

    if success:
        logger.info("Saved customer: %s", name)
        return f"Dhanyavaad. Main {name} ko yaad rakhta hoon."
    else:
        logger.error("Failed to save customer: %s", name)
        return "Maafi chahta hoon, data save nahi ho paya."


# ── Stock validation tool ─────────────────────────────────────────────────


@function_tool
async def check_stock(
    context: RunContext,
    product_name: str,
    requested_qty: int,
) -> str:
    """Check whether enough stock exists to fulfil a customer's requested quantity.

    ALWAYS call this before confirming any order or telling a customer their order is placed.
    Never assume stock is available based on the catalogue listing alone.

    Args:
        product_name: Name of the product as the customer said it (e.g., "Aashirvaad Atta")
        requested_qty: Number of units the customer wants to order
    """
    logger.info("Stock check — product=%r  qty=%d", product_name, requested_qty)

    try:
        results = get_product_stock(product_name)

        if not results:
            return (
                f"Product '{product_name}' not found in catalogue. "
                "Tell the customer this item is not available right now."
            )

        # Use the closest match (first result)
        product = results[0]
        available = product["qty"]
        name = product["name"]
        size = product["size"]
        price = product["price"]

        if available == 0:
            return (
                f"OUT_OF_STOCK: {name} {size} is currently out of stock. "
                "Tell the customer it's not available right now and offer an alternative if possible."
            )

        if requested_qty > available:
            return (
                f"INSUFFICIENT_STOCK: Customer wants {requested_qty} of {name} {size} "
                f"but only {available} are in stock. "
                f"Tell the customer: 'Abhi sirf {available} available hai. "
                f"Kya {available} se kaam chalega?' "
                f"Do NOT confirm an order for {requested_qty} units."
            )

        # Stock is sufficient
        total = int(price * requested_qty)
        return (
            f"STOCK_OK: {requested_qty}x {name} {size} @ ₹{int(price)} each = ₹{total} total. "
            f"Stock available: {available}. "
            "Proceed to confirm delivery address."
        )

    except Exception as exc:
        logger.error("check_stock failed: %s", exc, exc_info=True)
        return (
            "TOOL_ERROR: Could not verify stock right now. "
            "Do not confirm the order. Tell customer: "
            "'Abhi stock verify nahi ho pa raha. Thodi der mein try karein.'"
        )


# ── Catalogue tool ────────────────────────────────────────────────────────


@function_tool
async def lookup_catalogue(
    context: RunContext,
    query: str,
    category: Optional[str] = None,
) -> str:
    """Look up live product stock, prices, and availability from the store catalogue.

    Call this whenever a customer asks about:
    - Whether a specific product is available
    - The price of any item
    - What products are in a category (e.g., "kya oil mein kya hai?")
    - Quantity in stock (e.g., "kitna bachi hai?")

    Do NOT call this for general conversation. Only call when product data is needed.
    If this tool fails or returns no results, say honestly the item is not available right now.

    Args:
        query: Product name or keyword to search (e.g., "atta", "amul butter", "toor dal")
        category: Optional category filter (e.g., "Oil & Ghee", "Dairy", "Biscuits & Snacks")
    """
    logger.info("Catalogue lookup — query=%r  category=%r", query, category)

    try:
        if category:
            results = get_products_by_category(category)
            # further filter by query within category
            if query.strip():
                q = query.strip().lower()
                results = [r for r in results if q in r["name"].lower()]
        else:
            results = search_products(query)

        if not results:
            logger.info("No products found for query=%r", query)
            return "no_results"

        # Build a compact spoken summary (not JSON, not a list)
        # The agent will read this naturally
        lines = []
        for p in results[:5]:  # cap at 5 so the agent doesn't list 50 items
            stock_note = ""
            if p["qty"] == 0:
                stock_note = " (out of stock)"
            elif p["qty"] <= 5:
                stock_note = f" (only {p['qty']} left)"

            lines.append(
                f"{p['name']} {p['size']} — ₹{int(p['price'])}{stock_note}"
            )

        summary = "; ".join(lines)
        logger.info("Catalogue result: %s", summary)
        return summary

    except Exception as exc:
        logger.error("lookup_catalogue failed: %s", exc, exc_info=True)
        # Graceful spoken fallback — agent will say this
        return "tool_error: Abhi stock jankari nahi mil rahi. Thodi der baad try karein."