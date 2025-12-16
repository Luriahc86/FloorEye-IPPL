"""Email service for FloorEye notifications."""
import os
import ssl
import smtplib
from email.message import EmailMessage
import traceback
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Load from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")

if not SMTP_USER or not SMTP_PASSWORD:
    logger.warning("SMTP credentials missing; email sending will fail")


def send_email(
    subject: str,
    body: str,
    to_list: List[str],
    attachments: Optional[List[str]] = None,
) -> bool:
    """
    Send email with optional file attachments.
    
    Args:
        subject: Email subject
        body: Email body text
        to_list: List of recipient emails
        attachments: List of file paths to attach (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP credentials not configured")
        return False

    if not to_list:
        logger.error("No recipients specified")
        return False

    try:
        logger.info(f"Sending email to {len(to_list)} recipients: {subject}")
        
        msg = EmailMessage()
        msg["From"] = SMTP_FROM_EMAIL or SMTP_USER
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

        # Attach files if provided
        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, "rb") as f:
                        file_data = f.read()
                        filename = os.path.basename(filepath)
                        
                        # Determine mime type from extension
                        if filepath.endswith((".jpg", ".jpeg")):
                            maintype, subtype = "image", "jpeg"
                        elif filepath.endswith(".png"):
                            maintype, subtype = "image", "png"
                        else:
                            maintype, subtype = "application", "octet-stream"
                        
                        msg.add_attachment(
                            file_data,
                            maintype=maintype,
                            subtype=subtype,
                            filename=filename,
                        )
                        logger.info(f"Attached file: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to attach {filepath}: {e}")

        context = ssl.create_default_context()

        # Try STARTTLS first
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            logger.info("Email sent successfully via STARTTLS")
            return True

        except Exception as e1:
            logger.warning(f"STARTTLS failed: {e1}. Trying SMTP_SSL on port 465...")
            
            # Fallback to SSL
            try:
                with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=20) as server:
                    server.ehlo()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info("Email sent successfully via SMTP_SSL")
                return True
            except Exception as e2:
                logger.error(f"SMTP_SSL also failed: {e2}")
                traceback.print_exc()
                return False

    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        traceback.print_exc()
        return False
