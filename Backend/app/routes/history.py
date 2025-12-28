"""History routes for viewing detection events."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import Response
import logging

from app.store.db import get_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()


# =========================
# Schemas
# =========================
class HistoryItem(BaseModel):
    id: int
    source: str
    is_dirty: bool
    confidence: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


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
@router.get("/", response_model=List[HistoryItem])
def get_history(limit: int = 50, offset: int = 0):
    """Fetch detection history."""
    _require_db()

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                source,
                is_dirty,
                confidence,
                notes,
                created_at
            FROM floor_events
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )

        rows = cursor.fetchall()

        return [
            HistoryItem(
                id=r["id"],
                source=r["source"],
                is_dirty=bool(r["is_dirty"]),
                confidence=r.get("confidence"),
                notes=r.get("notes"),
                created_at=(
                    r["created_at"].isoformat()
                    if r.get("created_at")
                    else None
                ),
            )
            for r in rows
        ]

    except Exception as e:
        logger.exception("get_history failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/{event_id}/image")
def get_image(event_id: int):
    """Get image data from database event."""
    _require_db()

    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_data FROM floor_events WHERE id=%s",
            (event_id,),
        )
        row = cursor.fetchone()

        if not row or not row[0]:
            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )

        return Response(
            content=row[0],
            media_type="image/jpeg",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("get_image failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
