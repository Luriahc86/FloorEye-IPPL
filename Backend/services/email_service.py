import os
import ssl
import smtplib
from email.message import EmailMessage
import traceback
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

if not SMTP_USER or not SMTP_PASS:
    print("[WARN] SMTP credentials missing")


def send_email(
    subject: str,
    body: str,
    to_list: list[str],
    attachments_bytes: list[dict] | None = None,
):
    """
    attachments_bytes = [
        {
            "filename": "event_12.jpg",
            "data": b"...",
            "maintype": "image",
            "subtype": "jpeg"
        }
    ]
    """

    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] SMTP credentials not configured")
        return False

    if not to_list:
        print("[ERROR] No recipients")
        return False

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

        # 🔥 Attach from BYTES (NO FILESYSTEM)
        if attachments_bytes:
            for att in attachments_bytes:
                msg.add_attachment(
                    att["data"],
                    maintype=att.get("maintype", "application"),
                    subtype=att.get("subtype", "octet-stream"),
                    filename=att["filename"],
                )

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            return True

        except Exception:
            # fallback SSL 465
            with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=20) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            return True

    except Exception as e:
        print("[ERROR] send_email failed:", e)
        traceback.print_exc()
        return False
