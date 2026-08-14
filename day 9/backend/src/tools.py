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
import re
from typing import Optional

from livekit.agents import RunContext, function_tool

from database import get_user, save_user
from database_escalations import (
    create_escalation as db_create_escalation,
)
from database_escalations import (
    get_escalation_by_user_and_reason,
    mark_email_sent,
)
from database_orders import create_order as db_create_order
from database_orders import get_orders_by_user
from database_products import get_products_by_category, search_products
from email_notifier import send_escalation_email

logger = logging.getLogger("tools")


# ── Translation map for Hindi queries ─────────────────────────────────────

# Map common Hindi product terms to English equivalents for database searching
HINDI_TO_ENGLISH_PRODUCT_MAP = {
    "मैदा": "maida",
    "आटा": "atta",
    "बेसन": "besan",
    "सूजी": "sooji",
    "तेल": "oil",
    "मक्खन": "butter",
    "चीज़": "cheese",
    "घी": "ghee",
    "चावल": "rice",
    "दाल": "dal",
    "चीनी": "sugar",
    "नमक": "salt",
    "हल्दी": "haldi",
    "मिर्च": "mirch",
    "धनिया": "dhania",
    "जीरा": "jeera",
    "गरम मसाला": "garam masala",
    "बिस्कुट": "biscuit",
    "चाय": "tea",
    "कॉफी": "coffee",
    "दूध": "milk",
    "दही": "dahi",
    "पनीर": "paneer",
    "आलू": "potato",
    "प्याज": "onion",
    "टमाटर": "tomato",
    "भुजिया": "bhujia",
    "नमकीन": "namkeen",
    "कोल्ड ड्रिंक": "cold drink",
    "पानी": "water",
    "तेल सरसों": "mustard oil",
    "सरसों तेल": "mustard oil",
    "मूंगफली तेल": "groundnut oil",
    "सूरजमुखी तेल": "sunflower oil",
}


def translate_query_for_db(query: str) -> str:
    """Convert Hindi product terms to English for database lookup.

    If the query contains Devanagari script, try to map it to English.
    Otherwise return the query as-is.
    """
    import re

    # Remove leading quantity indicators like "1x ", "2x", etc.
    query = re.sub(r"^\d+[xX]\s*", "", query.strip())
    query_lower = query.strip().lower()

    # Check if query contains Devanagari characters
    has_devanagari = any("\u0900" <= char <= "\u097f" for char in query)

    if has_devanagari:
        # Try direct mapping first
        if query_lower in HINDI_TO_ENGLISH_PRODUCT_MAP:
            translated = HINDI_TO_ENGLISH_PRODUCT_MAP[query_lower]
            logger.info("Translated Hindi query '%s' → '%s'", query, translated)
            return translated

        # Try partial matching for multi-word queries
        for hindi_term, english_term in HINDI_TO_ENGLISH_PRODUCT_MAP.items():
            if hindi_term in query_lower:
                logger.info(
                    "Partial translation: '%s' → '%s' (matched '%s')",
                    query,
                    english_term,
                    hindi_term,
                )
                return english_term

    # If no Devanagari or no match found, return original query
    return query


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
        return "Successfully saved customer profile."
    else:
        logger.error("Failed to save customer: %s", name)
        return "Failed to save customer profile. Agent should tell customer naturally that saving didn't work."


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
        # Translate Hindi product names to English for DB lookup
        search_name = translate_query_for_db(product_name)
        results = search_products(search_name)
        if not results and search_name != product_name:
            results = search_products(product_name)

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
                f"Tell the customer the available quantity and ask if they want that instead. "
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
            "Do not confirm the order. Tell customer to try again later."
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
        # Translate Hindi queries to English for database lookup
        search_query = translate_query_for_db(query)

        if category:
            results = get_products_by_category(category)
            # further filter by query within category
            if search_query.strip():
                q = search_query.strip().lower()
                results = [r for r in results if q in r["name"].lower()]
        else:
            results = search_products(search_query)

            # If no results with translated query, try original query
            if not results and search_query != query:
                logger.info(
                    "No results with translated query, trying original: %r", query
                )
                results = search_products(query)

        if not results:
            logger.info(
                "No products found for query=%r (translated=%r)", query, search_query
            )
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

            lines.append(f"{p['name']} {p['size']} — ₹{int(p['price'])}{stock_note}")

        summary = "; ".join(lines)
        logger.info("Catalogue result: %s", summary)
        return summary

    except Exception as exc:
        logger.error("lookup_catalogue failed: %s", exc, exc_info=True)
        # Graceful spoken fallback — agent will say this
        return "tool_error: Could not fetch product information. Tell customer to try again later."


@function_tool
async def place_order(
    context: RunContext,
    user_id: str,
    customer_name: str,
    customer_phone: str,
    delivery_address: str,
    items_json: str,
    total_amount: float,
    delivery_date: str,
    delivery_slot: str = "morning",
    payment_method: str = "cod",
) -> str:
    """Save a completed order to the database. ONLY call this after ALL items pass check_stock and the customer confirms the order.

    Args:
        user_id: The customer's unique ID from the session
        customer_name: Customer's full name
        customer_phone: Customer's phone number for delivery calls (e.g., "sip:kavan" or "+91...")
        delivery_address: Full delivery address
        items_json: JSON string of items — [{"product_name": "...", "qty": 2, "price": 295}, ...]
        total_amount: Total order amount in rupees
        delivery_date: Delivery date as YYYY-MM-DD (usually tomorrow's date)
        delivery_slot: morning, afternoon, or evening
        payment_method: cod, gpay, phonepe, or paytm
    """
    import json as json_mod
    from datetime import date

    logger.info(
        "Placing order for %s — %d items, ₹%d, delivery %s",
        customer_name,
        len(json_mod.loads(items_json)),
        int(total_amount),
        delivery_date,
    )

    # Generate a simple order ID
    today = date.today().isoformat().replace("-", "")

    # Count existing orders today for sequential numbering
    try:
        existing = get_orders_by_user(user_id)
        today_orders = [o for o in existing if o["order_id"].startswith(f"ORD-{today}")]
        seq = len(today_orders) + 1
    except Exception:
        seq = 1

    order_id = f"ORD-{today}-{seq:03d}"

    try:
        items = json_mod.loads(items_json)
    except json_mod.JSONDecodeError:
        logger.error("Invalid items_json: %s", items_json)
        return "ERROR: Invalid items format. Agent should tell customer there was a problem saving the order."

    success = db_create_order(
        order_id=order_id,
        user_id=user_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        delivery_date=delivery_date,
        items=items,
        total_amount=total_amount,
        delivery_slot=delivery_slot,
        payment_method=payment_method,
    )

    if success:
        logger.info("Order saved successfully: %s", order_id)

        # Day 8: Mark this session as having a successful order
        # This flag is read at session end to record "success" outcome
        if hasattr(context, "session"):
            if not hasattr(context.session, "custom_data"):
                context.session.custom_data = {}
            context.session.custom_data["order_placed"] = True
            logger.info("Set order_placed flag for call analytics")

        return (
            f"Order {order_id} placed successfully. "
            f"Tell the customer their order ID is {order_id} and it will be delivered on {delivery_date} during the {delivery_slot} slot. "
            f"Our delivery agent will call one day before to confirm."
        )
    else:
        logger.error("Failed to save order: %s", order_id)
        return "ERROR: Could not save the order. Tell the customer to try again or call the store directly."


# ── PII stripping helper ──────────────────────────────────────────────────

# Patterns for sensitive data that must NOT be included in escalation summaries
_PII_PATTERNS = [
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD REMOVED]"),  # Card numbers
    (r"\b\d{3,4}[\s-]?\d{3,4}[\s-]?\d{3,4}\b", "[ACCOUNT REMOVED]"),  # Account numbers
    (r"\bOTP[:\s]*\d{4,8}\b", "[OTP REMOVED]", re.IGNORECASE),  # OTPs
    (r"\bPIN[:\s]*\d{4,6}\b", "[PIN REMOVED]", re.IGNORECASE),  # PINs
    (
        r"\b\d{4,6}\s*(?:otp|pin)\b",
        "[SENSITIVE REMOVED]",
        re.IGNORECASE,
    ),  # Reverse OTP/PIN
    (r"\bCVV[:\s]*\d{3,4}\b", "[CVV REMOVED]", re.IGNORECASE),  # CVV
    (r"\bUPI[:\s]*\S+@\S+\b", "[UPI REMOVED]", re.IGNORECASE),  # UPI IDs
]


def _strip_pii(text: str) -> str:
    """Remove sensitive information from escalation summaries.

    Strips: card numbers, account numbers, OTPs, PINs, CVVs, UPI IDs.
    """
    cleaned = text
    for pattern_tuple in _PII_PATTERNS:
        if len(pattern_tuple) == 3:
            pattern, replacement, flags = pattern_tuple
            cleaned = re.sub(pattern, replacement, cleaned, flags=flags)
        else:
            pattern, replacement = pattern_tuple
            cleaned = re.sub(pattern, replacement, cleaned)
    return cleaned


# ── Escalation tool (Day 7) ───────────────────────────────────────────────


@function_tool
async def create_escalation(
    context: RunContext,
    user_id: str,
    customer_name: str,
    reason: str,
    summary: str,
    what_agent_checked: str,
    urgency: str = "medium",
    language: str = "en",
    preferred_followup: str = "call",
) -> str:
    """Create a human-help escalation request. ONLY call this AFTER the customer
    has given explicit permission to share their information.

    Call this when:
    - The customer has a payment dispute (paid but order shows pending, wrong amount charged)
    - The customer wants a refund
    - The customer has an order dispute (wrong items delivered, order never arrived, damaged items)

    Do NOT call this for:
    - Normal product inquiries
    - Regular order placement
    - Stock availability questions
    - General conversation

    IMPORTANT: Before calling this tool, you MUST:
    1. Tell the customer what information you want to send
    2. Ask for their explicit permission
    3. Only proceed if they clearly say yes

    Args:
        user_id: The customer's unique ID from the session
        customer_name: Customer's name
        reason: One of: payment_dispute, refund_request, order_dispute
        summary: Short summary of the issue (who needs help, what happened).
                 Do NOT include passwords, OTPs, PINs, account numbers, or card details.
        what_agent_checked: What the agent already verified (e.g., "Checked order ORD-20260812-001,
                           status shows confirmed, payment shows pending")
        urgency: One of: low, medium, high, emergency.
                 Use 'high' for payment issues, 'emergency' only for fraud reports.
        language: Customer's language (en, hi, gu)
        preferred_followup: How they want to be contacted: call, whatsapp, or email
    """
    logger.info(
        "Creating escalation for %s — reason=%s, urgency=%s",
        customer_name,
        reason,
        urgency,
    )

    # Validate reason
    valid_reasons = {"payment_dispute", "refund_request", "order_dispute"}
    if reason not in valid_reasons:
        return (
            f"ERROR: Invalid reason '{reason}'. "
            f"Must be one of: {', '.join(valid_reasons)}. "
            "Tell the customer you are having a technical issue and to call the store directly."
        )

    # Validate urgency
    valid_urgencies = {"low", "medium", "high", "emergency"}
    if urgency not in valid_urgencies:
        urgency = "medium"

    # Strip PII from summary and what_agent_checked
    clean_summary = _strip_pii(summary)
    clean_checked = _strip_pii(what_agent_checked)

    # Check for duplicate open escalation
    existing = get_escalation_by_user_and_reason(user_id, reason)
    if existing:
        existing_id = existing["escalation_id"]
        logger.info(
            "Duplicate escalation found: %s (user=%s, reason=%s)",
            existing_id,
            user_id,
            reason,
        )
        return (
            f"DUPLICATE: An open request already exists — {existing_id}. "
            f"Tell the customer their earlier request (reference {existing_id}) is still being reviewed. "
            "Do not create a new request. Reassure them someone will follow up."
        )

    # Create the escalation in the database
    escalation_id = db_create_escalation(
        user_id=user_id,
        customer_name=customer_name,
        reason=reason,
        summary=clean_summary,
        what_agent_checked=clean_checked,
        urgency=urgency,
        language=language,
        preferred_followup=preferred_followup,
    )

    if not escalation_id:
        logger.error("Failed to create escalation for %s", customer_name)
        return (
            "ERROR: Could not create the request. "
            "Tell the customer to call the store directly at 098250-XXXXX."
        )

    # Send email notification via Gmail SMTP
    email_sent = await send_escalation_email(
        escalation_id=escalation_id,
        customer_name=customer_name,
        reason=reason,
        urgency=urgency,
        summary=clean_summary,
        what_agent_checked=clean_checked,
        language=language,
        preferred_followup=preferred_followup,
    )

    if email_sent:
        mark_email_sent(escalation_id)
        logger.info("Escalation email sent for %s", escalation_id)
    else:
        logger.warning(
            "Escalation email NOT sent for %s (saved to DB only)", escalation_id
        )

    # Build response for the agent
    reason_display = reason.replace("_", " ")
    return (
        f"ESCALATION_CREATED: Reference ID is {escalation_id}. "
        f"Tell the customer: 'Your request has been created. "
        f"Your reference number is {escalation_id}. "
        f"Someone from the store will review your {reason_display} and contact you "
        f"via {preferred_followup} within 2 to 4 hours during business hours (8 AM to 10 PM). "
        f"Please keep this reference number for follow-up.' "
        "Do NOT promise an immediate response. Be honest about the timeline."
    )
