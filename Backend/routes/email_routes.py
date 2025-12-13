from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from store.db import get_connection
from services.email_service import send_email

router = APIRouter()

class EmailRecipient(BaseModel):
    email: str
    active: bool = True


class EmailRecipientPatch(BaseModel):
    active: bool

@router.get("/")
def list_recipients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM email_recipients ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@router.post("/")
def create_recipient(payload: EmailRecipient):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO email_recipients (email, active) VALUES (%s, %s)",
        (payload.email, payload.active),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Recipient added"}

@router.patch("/{rid}")
def patch_recipient(rid: int, payload: EmailRecipientPatch):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE email_recipients SET active=%s WHERE id=%s",
        (payload.active, rid),
    )

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(404, "Recipient not found")

    conn.commit()

    cursor.execute("SELECT * FROM email_recipients WHERE id=%s", (rid,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(404, "Recipient not found")

    return row

@router.delete("/{rid}")
def delete_recipient(rid: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM email_recipients WHERE id=%s", (rid,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Deleted"}

@router.get("/test")
def test_email():
    """Send test email to all active recipients."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email FROM email_recipients WHERE active = 1")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return {"sent": False, "message": "No active recipients"}

    emails = [r["email"] for r in rows]
    ok = send_email(
        "[FloorEye] Test Email",
        "Ini adalah email test dari FloorEye. Jika kamu menerima ini, email notifikasi berhasil dikonfigurasi!",
        emails
    )

    if ok:
        return {"sent": True, "recipients": emails}
    else:
        raise HTTPException(500, "Failed to send email; check server logs")
