import os
import logging
import base64
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "FloorEye <onboarding@resend.dev>")

SMTP_ENABLED = bool(RESEND_API_KEY)

logger.info(f"[EMAILER] RESEND_API_KEY={'SET' if RESEND_API_KEY else 'NOT SET'}")
logger.info(f"[EMAILER] EMAIL_FROM={EMAIL_FROM}")
logger.info(f"[EMAILER] EMAIL_ENABLED={SMTP_ENABLED}")

if not SMTP_ENABLED:
    logger.warning("[EMAILER] Resend API key not configured - email sending disabled")


def send_email(
    subject: str,
    body: str,
    to_list: List[str],
    image_data: Optional[bytes] = None,
    image_filename: str = "detection.jpg",
) -> bool:
    if not SMTP_ENABLED:
        logger.error("[EMAIL] Resend API key missing")
        return False

    if not to_list:
        logger.error("[EMAIL] No email recipients provided")
        return False

    logger.info(f"[EMAIL] Attempting to send email to {to_list}")

    try:
        payload = {
            "from": EMAIL_FROM,
            "to": to_list,
            "subject": subject,
            "text": body,
        }

        if image_data:
            try:
                content_b64 = base64.b64encode(image_data).decode("utf-8")
                payload["attachments"] = [
                    {
                        "filename": image_filename,
                        "content": content_b64,
                    }
                ]
                logger.info(f"[EMAIL] Attached image: {image_filename} ({len(image_data)} bytes)")
            except Exception as e:
                logger.warning(f"[EMAIL] Failed to attach image: {e}")

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"[EMAIL] Email sent successfully! ID: {result.get('id')}")
            return True
        else:
            logger.error(f"[EMAIL] Resend API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"[EMAIL] Email sending failed: {type(e).__name__}: {e}")
        return False
