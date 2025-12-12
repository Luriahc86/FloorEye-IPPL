from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from store.db import get_connection
from services.email_service import send_email

router = APIRouter()


# =========================
# Schemas
# =========================
class EmailRecipient(BaseModel):
    email: EmailStr
    active: bool = True


# =========================
# Routes
# =========================
@router.get("/")
def list_recipients():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM email_recipients ORDER BY id DESC")
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def create_recipient(payload: EmailRecipient):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_recipients (email, active)
            VALUES (%s, %s)
            """,
            (payload.email, int(payload.active)),
        )
        conn.commit()
        return {"message": "Recipient added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.patch("/{rid}")
def patch_recipient(rid: int, body: Dict[str, Any]):
    if "active" not in body:
        raise HTTPException(status_code=400, detail="Missing 'active' field")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE email_recipients SET active = %s WHERE id = %s",
            (int(body["active"]), rid),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipient not found")

        return {"message": "Updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{rid}")
def delete_recipient(rid: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM email_recipients WHERE id = %s", (rid,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipient not found")

        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/test")
def test_email():
    """Send test email to all active recipients."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT email FROM email_recipients WHERE active = 1"
        )
        rows = cursor.fetchall()

        if not rows:
            return {"sent": False, "message": "No active recipients"}

        emails = [r["email"] for r in rows]

        ok = send_email(
            subject="[FloorEye] Test Email",
            body=(
                "Ini adalah email test dari FloorEye.\n\n"
                "Jika kamu menerima email ini, berarti konfigurasi "
                "notifikasi email sudah berhasil."
            ),
            to_list=emails,
        )

        if not ok:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email; check server logs"
            )

        return {"sent": True, "recipients": emails}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
