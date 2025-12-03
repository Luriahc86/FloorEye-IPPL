import os
import ssl
import smtplib
from email.message import EmailMessage
import traceback

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_email(subject, body, to_list, attachments=None):
    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] SMTP not configured")
        return False

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = subject
        msg.set_content(body)

        if attachments:
            for path in attachments:
                try:
                    with open(path, "rb") as f:
                        msg.add_attachment(
                            f.read(),
                            maintype="image",
                            subtype="jpeg",
                            filename=os.path.basename(path)
                        )
                except:
                    print(f"[WARN] Failed attach {path}")

        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print("[INFO] Email sent")
        return True

    except Exception as e:
        print("[ERROR] send_email:", e)
        traceback.print_exc()
        return False
