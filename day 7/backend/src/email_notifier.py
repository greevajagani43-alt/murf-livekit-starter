"""
email_notifier.py
─────────────────
Gmail SMTP email notifications for escalation requests (Day 7).

Sends a formatted email to the store owner when a human-help
request is created by the voice agent.

Environment variables (in .env.local):
    GMAIL_SENDER_EMAIL    — the Gmail address to send from
    GMAIL_APP_PASSWORD    — a Gmail App Password (not regular password)
    ESCALATION_NOTIFY_EMAIL — the recipient email for escalation alerts
"""

import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger("email_notifier")

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def _get_email_config() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Read email config from environment variables."""
    sender = os.environ.get("GMAIL_SENDER_EMAIL")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("ESCALATION_NOTIFY_EMAIL")
    return sender, password, recipient


def _urgency_emoji(urgency: str) -> str:
    """Return an emoji for the urgency level."""
    return {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "emergency": "🔴",
    }.get(urgency, "🟡")


def _build_email_html(
    escalation_id: str,
    customer_name: str,
    reason: str,
    urgency: str,
    summary: str,
    what_agent_checked: str,
    language: str,
    preferred_followup: str,
) -> str:
    """Build a clean HTML email body for the escalation notification."""
    emoji = _urgency_emoji(urgency)
    reason_display = reason.replace("_", " ").title()

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f8f9fa; border-left: 4px solid {"#dc3545" if urgency in ("high", "emergency") else "#ffc107"}; padding: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0 0 5px 0; color: #333;">
                {emoji} New Escalation Request — {escalation_id}
            </h2>
            <p style="margin: 0; color: #666; font-size: 14px;">
                Ratan Kirana & General Store — Saathi Voice Agent
            </p>
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="padding: 8px 12px; background: #f1f3f5; font-weight: bold; width: 160px;">Customer Name</td>
                <td style="padding: 8px 12px;">{customer_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px 12px; background: #f1f3f5; font-weight: bold;">Reason</td>
                <td style="padding: 8px 12px;">{reason_display}</td>
            </tr>
            <tr>
                <td style="padding: 8px 12px; background: #f1f3f5; font-weight: bold;">Urgency</td>
                <td style="padding: 8px 12px;">{emoji} {urgency.upper()}</td>
            </tr>
            <tr>
                <td style="padding: 8px 12px; background: #f1f3f5; font-weight: bold;">Language</td>
                <td style="padding: 8px 12px;">{language}</td>
            </tr>
            <tr>
                <td style="padding: 8px 12px; background: #f1f3f5; font-weight: bold;">Preferred Follow-up</td>
                <td style="padding: 8px 12px;">{preferred_followup}</td>
            </tr>
        </table>

        <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 12px; margin-bottom: 15px;">
            <h3 style="margin: 0 0 8px 0; color: #856404;">Issue Summary</h3>
            <p style="margin: 0; color: #856404;">{summary}</p>
        </div>

        <div style="background: #d1ecf1; border: 1px solid #17a2b8; border-radius: 4px; padding: 12px; margin-bottom: 15px;">
            <h3 style="margin: 0 0 8px 0; color: #0c5460;">What the Agent Already Checked</h3>
            <p style="margin: 0; color: #0c5460;">{what_agent_checked if what_agent_checked else "No prior checks noted."}</p>
        </div>

        <div style="background: #e2e3e5; border-radius: 4px; padding: 12px; text-align: center;">
            <p style="margin: 0; color: #383d41; font-size: 12px;">
                Reference ID: <strong>{escalation_id}</strong><br>
                This request was created by the Saathi voice assistant.
                Please review and contact the customer.
            </p>
        </div>
    </body>
    </html>
    """


def _send_email_sync(
    escalation_id: str,
    customer_name: str,
    reason: str,
    urgency: str,
    summary: str,
    what_agent_checked: str,
    language: str,
    preferred_followup: str,
) -> bool:
    """Send escalation email synchronously via Gmail SMTP.

    Returns True if sent successfully, False otherwise.
    """
    sender, password, recipient = _get_email_config()

    if not all([sender, password, recipient]):
        logger.warning(
            "Email not configured — missing GMAIL_SENDER_EMAIL, "
            "GMAIL_APP_PASSWORD, or ESCALATION_NOTIFY_EMAIL. "
            "Escalation saved to DB but email not sent."
        )
        return False

    try:
        # Build the email
        msg = MIMEMultipart("alternative")
        reason_display = reason.replace("_", " ").title()
        emoji = _urgency_emoji(urgency)

        msg["Subject"] = (
            f"{emoji} [{urgency.upper()}] Escalation {escalation_id} — "
            f"{reason_display} — {customer_name}"
        )
        msg["From"] = sender
        msg["To"] = recipient

        # Plain text fallback
        plain_text = (
            f"New Escalation: {escalation_id}\n"
            f"Customer: {customer_name}\n"
            f"Reason: {reason_display}\n"
            f"Urgency: {urgency.upper()}\n"
            f"Language: {language}\n"
            f"Follow-up: {preferred_followup}\n\n"
            f"Summary: {summary}\n\n"
            f"Agent checked: {what_agent_checked}\n"
        )
        msg.attach(MIMEText(plain_text, "plain"))

        # HTML version
        html = _build_email_html(
            escalation_id=escalation_id,
            customer_name=customer_name,
            reason=reason,
            urgency=urgency,
            summary=summary,
            what_agent_checked=what_agent_checked,
            language=language,
            preferred_followup=preferred_followup,
        )
        msg.attach(MIMEText(html, "html"))

        # Send via Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())

        logger.info("Escalation email sent: %s → %s", escalation_id, recipient)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail SMTP authentication failed. "
            "Check GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD in .env.local. "
            "Make sure you're using a Gmail App Password, not your regular password."
        )
        return False
    except Exception as e:
        logger.error(f"Failed to send escalation email: {e}")
        return False


async def send_escalation_email(
    escalation_id: str,
    customer_name: str,
    reason: str,
    urgency: str,
    summary: str,
    what_agent_checked: str,
    language: str,
    preferred_followup: str,
) -> bool:
    """Send escalation email asynchronously (runs in thread executor).

    This is the primary public API. It wraps the synchronous SMTP call
    in an executor so it doesn't block the async event loop.

    Returns True if sent successfully, False otherwise.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _send_email_sync,
        escalation_id,
        customer_name,
        reason,
        urgency,
        summary,
        what_agent_checked,
        language,
        preferred_followup,
    )
