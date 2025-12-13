import os
import ssl
import smtplib
from email.message import EmailMessage
import traceback
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

if not SMTP_USER or not SMTP_PASS:
    print("[WARN] SMTP credentials missing; email sending will fail.")


def send_email(
    subject: str,
    body: str,
    to_list: List[str],
    attachments: List[Dict] | None = None,
):
    """
    Send email with optional in-memory attachments.

    attachments format:
    [
        {
            "filename": "event_123.jpg",
            "content": bytes,
            "mime": "image/jpeg"
        }
    ]
    """

    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] SMTP credentials not configured")
        return False

    if not to_list:
        print("[ERROR] No recipients provided")
        return False

    try:
        print(f"[INFO] Building email: to={to_list}, subject={subject}")

        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

        # 🔥 Attach from MEMORY (NO FILE SYSTEM)
        if attachments:
            for att in attachments:
                try:
                    maintype, subtype = att["mime"].split("/", 1)
                    msg.add_attachment(
                        att["content"],
                        maintype=maintype,
                        subtype=subtype,
                        filename=att["filename"],
                    )
                    print(f"[INFO] Attached (memory): {att['filename']}")
                except Exception as e:
                    print(f"[WARN] Failed to attach memory file {att}: {e}")

        context = ssl.create_default_context()

        print(f"[INFO] Connecting to SMTP {SMTP_HOST}:{SMTP_PORT}")
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                print("[INFO] EHLO sent")
                server.starttls(context=context)
                print("[INFO] STARTTLS OK")
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                print("[INFO] Login OK")
                server.send_message(msg)
                print("[INFO] Message sent via STARTTLS")
            return True

        except Exception as e1:
            print(f"[WARN] STARTTLS failed: {e1}. Trying SMTP_SSL on port 465...")
            try:
                with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=20) as server:
                    server.ehlo()
                    print("[INFO] EHLO sent (SSL)")
                    server.login(SMTP_USER, SMTP_PASS)
                    print("[INFO] Login OK (SSL)")
                    server.send_message(msg)
                    print("[INFO] Message sent via SMTP_SSL")
                return True
            except Exception as e2:
                print(f"[ERROR] SMTP_SSL also failed: {e2}")
                traceback.print_exc()
                return False

    except Exception as e:
        print("[ERROR] send_email outer exception:", e)
        traceback.print_exc()
        return False
