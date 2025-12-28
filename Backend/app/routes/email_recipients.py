"""Email recipient management routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import logging

from app.store.db import get_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()

# =========================
# Optional email service
# =========================
try:
    from app.services.emailer import send_email
    EMAIL_AVAILABLE = True
except Exception as e:
    logger.warning(f"Email service unavailable: {e}")
    EMAIL_AVAILABLE = False


# =========================
# Schemas
# =========================
class EmailRecipient(BaseModel):
    email: EmailStr
    active: bool = True


class EmailRecipientPatch(BaseModel):
    active: bool


# =========================
# Helpers
# =========================
def _require_db():
    if not ENABLE_DB:
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )


# =========================
# Routes
# =========================
@router.get("/")
def list_recipients():
    """List all email recipients."""
    _require_db()

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM email_recipients ORDER BY id DESC"
        )
        return cursor.fetchall()

    except Exception as e:
        logger.exception("list_recipients failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/")
def create_recipient(payload: EmailRecipient):
    """Add new email recipient."""
    _require_db()

    conn = cursor = None
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
        logger.exception("create_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.patch("/{rid}")
def patch_recipient(rid: int, payload: EmailRecipientPatch):
    """Update recipient active status."""
    _require_db()

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "UPDATE email_recipients SET active=%s WHERE id=%s",
            (int(payload.active), rid),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Recipient not found"
            )

        conn.commit()

        cursor.execute(
            "SELECT * FROM email_recipients WHERE id=%s",
            (rid,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Recipient not found"
            )

        return row

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("patch_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.delete("/{rid}")
def delete_recipient(rid: int):
    """Delete email recipient."""
    _require_db()

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM email_recipients WHERE id=%s",
            (rid,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Recipient not found"
            )

        return {"message": "Deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("delete_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/test")
def test_email():
    """Send test email to all active recipients."""
    _require_db()

    if not EMAIL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured"
        )

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT email FROM email_recipients WHERE active = 1"
        )
        rows = cursor.fetchall()

        if not rows:
            return {
                "sent": False,
                "message": "No active recipients"
            }

        emails = [r["email"] for r in rows]

        ok = send_email(
            subject="[FloorEye] Test Email",
            body=(
                "Ini adalah email test dari FloorEye.\n\n"
                "Jika kamu menerima email ini, berarti "
                "konfigurasi notifikasi email sudah berhasil."
            ),
            to_list=emails,
        )

        if not ok:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email; check server logs"
            )

        return {
            "sent": True,
            "recipients": emails
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("test_email failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
