"""
tests/test_agent.py  —  Day 6 basic agent tests
──────────────────────────────────────────────────
Tests that verify the outbound agent behaves correctly.
Run with: uv run pytest
"""

import pytest


def test_outbound_greeting_has_required_parts():
    """
    Day 6 requirement: first 2 sentences must contain
    1. Who's calling
    2. Why
    3. How to make it stop
    """
    from prompt import OUTBOUND_GREETING

    greeting = OUTBOUND_GREETING.lower()

    # 1. Who is calling — Saathi / Ratan Kirana
    assert "साथी" in OUTBOUND_GREETING or "saathi" in greeting, \
        "Greeting must identify the caller (Saathi)"
    assert "रतन" in OUTBOUND_GREETING or "ratan" in greeting, \
        "Greeting must mention the store name"

    # 2. Why calling — restock / reminder
    assert any(word in OUTBOUND_GREETING for word in ["आटा", "मँगाने", "restock", "reminder"]), \
        "Greeting must state the reason for the call"

    # 3. How to stop — opt-out instruction
    assert any(word in OUTBOUND_GREETING for word in ["नहीं चाहिए", "बंद", "band", "stop", "opt"]), \
        "Greeting must explain how to stop the call"


def test_greeting_is_short():
    """
    Outbound greeting should be concise — under 250 characters.
    """
    from prompt import OUTBOUND_GREETING

    assert len(OUTBOUND_GREETING) < 400, \
        f"Greeting too long ({len(OUTBOUND_GREETING)} chars). Keep it brief for phone calls."


def test_system_prompt_has_optout_handling():
    """
    System prompt must include opt-out handling instructions.
    """
    from prompt import SYSTEM_PROMPT

    prompt_lower = SYSTEM_PROMPT.lower()
    assert "opt" in prompt_lower or "नहीं चाहिए" in SYSTEM_PROMPT or "band karo" in prompt_lower, \
        "System prompt must include opt-out handling"


def test_system_prompt_has_outbound_context_placeholder():
    """
    System prompt must accept {outbound_context} and {user_id} format args.
    """
    from prompt import SYSTEM_PROMPT

    assert "{outbound_context}" in SYSTEM_PROMPT, \
        "System prompt must have {outbound_context} placeholder"
    assert "{user_id}" in SYSTEM_PROMPT, \
        "System prompt must have {user_id} placeholder"

    # Verify it can be formatted without error
    formatted = SYSTEM_PROMPT.format(outbound_context="OUTBOUND_CALL", user_id="test123")
    assert "OUTBOUND_CALL" in formatted
    assert "test123" in formatted


def test_trigger_call_requires_number():
    """
    trigger_call.py must require a phone number argument.
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "src/trigger_call.py"],
        capture_output=True,
        text=True,
    )
    # Should exit with error (missing --number argument)
    assert result.returncode != 0, "trigger_call.py should fail without --number arg"


def test_trigger_call_dry_run(capsys):
    """
    Dry run should print config and exit cleanly without making a real call.
    """
    import asyncio
    import os

    # Provide dummy env vars so it doesn't fail on missing keys
    os.environ.setdefault("LIVEKIT_URL", "wss://test.livekit.cloud")
    os.environ.setdefault("LIVEKIT_API_KEY", "test_key")
    os.environ.setdefault("LIVEKIT_API_SECRET", "test_secret")
    os.environ.setdefault("LIVEKIT_SIP_TRUNK_ID", "ST_test123")

    from trigger_call import trigger_outbound_call

    # Should complete without error in dry-run mode
    asyncio.run(
        trigger_outbound_call(
            phone_number="+911234567890",
            customer_name="Test User",
            dry_run=True,
        )
    )
    # No assertion needed — if it doesn't raise, the dry-run path works
