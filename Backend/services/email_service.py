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
<<<<<<< HEAD
    print("[WARN] SMTP credentials missing")
=======
    print("[WARN] SMTP credentials missing; email sending will fail.")
>>>>>>> dev


def send_email(
    subject: str,
    body: str,
<<<<<<< HEAD
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
=======
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
>>>>>>> dev
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
<<<<<<< HEAD
=======
        print(f"[INFO] Building email: to={to_list}, subject={subject}")

>>>>>>> dev
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

<<<<<<< HEAD
        # 🔥 Attach from BYTES (NO FILESYSTEM)
        if attachments_bytes:
            for att in attachments_bytes:
                msg.add_attachment(
                    att["data"],
                    maintype=att.get("maintype", "application"),
                    subtype=att.get("subtype", "octet-stream"),
                    filename=att["filename"],
                )
=======
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
>>>>>>> dev

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            return True

<<<<<<< HEAD
        except Exception:
            # fallback SSL 465
            with smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=20) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            return True
=======
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
>>>>>>> dev

    except Exception as e:
        print("[ERROR] send_email failed:", e)
        traceback.print_exc()
        return False
