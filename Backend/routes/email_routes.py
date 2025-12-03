from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from store.db import get_connection

router = APIRouter()

class EmailRecipient(BaseModel):
    email: str
    active: bool = True

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
def patch_recipient(rid: int, body: dict):
    if "active" not in body:
        raise HTTPException(400, "Missing 'active'")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE email_recipients SET active=%s WHERE id=%s",
        (body["active"], rid),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Updated"}
