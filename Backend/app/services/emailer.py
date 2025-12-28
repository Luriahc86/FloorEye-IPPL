"""
Email service for FloorEye notifications.
Handles SMTP with STARTTLS + SSL fallback.
"""

import os
import ssl
import smtplib
import logging
from email.message import EmailMessage
from typing import List, Optional

logger = logging.getLogger(__name__)

# =========================
# Environment config
# =========================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL") or SMTP_USER

SMTP_ENABLED = bool(SMTP_USER and SMTP_PASSWORD)

if not SMTP_ENABLED:
    logger.warning("SMTP not configured; email sending disabled")


# =========================
# Public API
# =========================
def send_email(
    subject: str,
    body: str,
    to_list: List[str],
    attachments: Optional[List[str]] = None,
) -> bool:
    """
    Send email with optional attachments.

    Returns:
        True if sent successfully, False otherwise
    """

    if not SMTP_ENABLED:
        logger.error("SMTP credentials missing")
        return False

    if not to_list:
        logger.error("No email recipients provided")
        return False

    try:
        msg = _build_message(
            subject=subject,
            body=body,
            to_list=to_list,
            attachments=attachments,
        )

        context = ssl.create_default_context()

        # Try STARTTLS first (587)
        try:
            _send_via_starttls(msg, context)
            logger.info("Email sent successfully via STARTTLS")
            return True

        except Exception as e:
            logger.warning(f"STARTTLS failed: {e}, trying SMTP_SSL")

            # Fallback to SSL (465)
            _send_via_ssl(msg, context)
            logger.info("Email sent successfully via SMTP_SSL")
            return True

    except Exception as e:
        logger.exception("Email sending failed")
        return False


# =========================
# Internal helpers
# =========================
def _build_message(
    subject: str,
    body: str,
    to_list: List[str],
    attachments: Optional[List[str]],
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    msg.set_content(body)

    if attachments:
        for path in attachments:
            _attach_file(msg, path)

    return msg


def _attach_file(msg: EmailMessage, filepath: str):
    try:
        with open(filepath, "rb") as f:
            data = f.read()

        filename = os.path.basename(filepath)
        maintype, subtype = _guess_mime_type(filename)

        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )

        logger.info(f"Attached file: {filename}")

    except Exception as e:
        logger.warning(f"Failed to attach file {filepath}: {e}")


def _guess_mime_type(filename: str):
    name = filename.lower()
    if name.endswith((".jpg", ".jpeg")):
        return "image", "jpeg"
    if name.endswith(".png"):
        return "image", "png"
    if name.endswith(".pdf"):
        return "application", "pdf"
    return "application", "octet-stream"


def _send_via_starttls(msg: EmailMessage, context: ssl.SSLContext):
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def _send_via_ssl(msg: EmailMessage, context: ssl.SSLContext):
    with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=20) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
