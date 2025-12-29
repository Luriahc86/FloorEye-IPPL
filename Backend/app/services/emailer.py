import os
import logging
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
    attachments: Optional[List[str]] = None,
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

        if attachments:
            attachment_list = []
            for filepath in attachments:
                try:
                    with open(filepath, "rb") as f:
                        import base64
                        content = base64.b64encode(f.read()).decode("utf-8")
                        filename = os.path.basename(filepath)
                        attachment_list.append({
                            "filename": filename,
                            "content": content,
                        })
                        logger.info(f"[EMAIL] Attached file: {filename}")
                except Exception as e:
                    logger.warning(f"[EMAIL] Failed to attach file {filepath}: {e}")

            if attachment_list:
                payload["attachments"] = attachment_list

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
