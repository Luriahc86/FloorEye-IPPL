from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import logging

from sqlalchemy import text
from app.store.db import get_db_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from app.services.emailer import send_email, SMTP_ENABLED
    EMAIL_AVAILABLE = SMTP_ENABLED
except Exception as e:
    logger.warning(f"Email service unavailable: {e}")
    EMAIL_AVAILABLE = False


class EmailRecipient(BaseModel):
    email: EmailStr
    active: bool = True


class EmailRecipientPatch(BaseModel):
    active: bool


def _require_db():
    if not ENABLE_DB:
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )


@router.get("")
def list_recipients():
    _require_db()

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT id, email, active, created_at FROM email_recipients ORDER BY id DESC")
            )
            rows = result.fetchall()

            return [
                {
                    "id": r[0],
                    "email": r[1],
                    "active": bool(r[2]),
                    "created_at": r[3].isoformat() if r[3] else None
                }
                for r in rows
            ]

    except Exception as e:
        logger.exception("list_recipients failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def create_recipient(payload: EmailRecipient):
    _require_db()

    try:
        with get_db_connection() as conn:
            existing = conn.execute(
                text("SELECT id FROM email_recipients WHERE email = :email"),
                {"email": payload.email}
            ).fetchone()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Email already exists"
                )

            conn.execute(
                text("""
                    INSERT INTO email_recipients (email, active)
                    VALUES (:email, :active)
                """),
                {"email": payload.email, "active": int(payload.active)}
            )
            conn.commit()

            return {"message": "Recipient added", "email": payload.email}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("create_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{rid}")
def patch_recipient(rid: int, payload: EmailRecipientPatch):
    _require_db()

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("UPDATE email_recipients SET active = :active WHERE id = :rid"),
                {"active": int(payload.active), "rid": rid}
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Recipient not found"
                )

            conn.commit()

            row = conn.execute(
                text("SELECT id, email, active, created_at FROM email_recipients WHERE id = :rid"),
                {"rid": rid}
            ).fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="Recipient not found"
                )

            return {
                "id": row[0],
                "email": row[1],
                "active": bool(row[2]),
                "created_at": row[3].isoformat() if row[3] else None
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("patch_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rid}")
def delete_recipient(rid: int):
    _require_db()

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("DELETE FROM email_recipients WHERE id = :rid"),
                {"rid": rid}
            )
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Recipient not found"
                )

            return {"message": "Deleted", "id": rid}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("delete_recipient failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
def test_email():
    _require_db()

    if not EMAIL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Check SMTP_USER and SMTP_PASSWORD environment variables."
        )

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT email FROM email_recipients WHERE active = 1")
            )
            rows = result.fetchall()

            if not rows:
                return {
                    "sent": False,
                    "message": "No active recipients"
                }

            emails = [r[0] for r in rows]

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


@router.get("/status")
def email_status():
    return {
        "email_available": EMAIL_AVAILABLE,
        "smtp_configured": EMAIL_AVAILABLE,
        "message": "Email service is ready" if EMAIL_AVAILABLE else "SMTP not configured - check SMTP_USER and SMTP_PASSWORD"
    }
