"""Email recipient management routes."""
from fastapi import APIRouter, HTTPSException
from pydantic import BaseModel, EmailStr
import logging

from app.store.db import get_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()

# Try to import email service
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class EmailRecipient(BaseModel):
    email: EmailStr
    active: bool = True


class EmailRecipientPatch(BaseModel):
    active: bool


@router.get("/")
def list_recipients():
    """List all email recipients."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM email_recipients ORDER BY id DESC")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"list_recipients error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/")
def create_recipient(payload: EmailRecipient):
    """Add new email recipient."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
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
        logger.error(f"create_recipient error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.patch("/{rid}")
def patch_recipient(rid: int, payload: EmailRecipientPatch):
    """Update recipient active status."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"patch_recipient error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rid}")
def delete_recipient(rid: int):
    """Delete email recipient."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    
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
        logger.error(f"delete_recipient error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/test")
def test_email():
    """Send test email to all active recipients."""
    if not ENABLE_DB:
        raise HTTPException(status_code=503, detail="Database not configured")
    if not EMAIL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Email service not configured")
    
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
                "Ini adalah email test dari FloorEye.\\n\\n"
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
        logger.error(f"test_email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
