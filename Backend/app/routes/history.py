from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import Response
import logging

from sqlalchemy import text
from app.store.db import get_db_connection
from app.utils.config import ENABLE_DB

logger = logging.getLogger(__name__)
router = APIRouter()


class HistoryItem(BaseModel):
    id: int
    source: str
    is_dirty: bool
    confidence: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


def _require_db():
    if not ENABLE_DB:
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )


@router.get("", response_model=List[HistoryItem])
def get_history(limit: int = 50, offset: int = 0):
    _require_db()

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        id,
                        source,
                        is_dirty,
                        confidence,
                        notes,
                        created_at
                    FROM floor_events
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"limit": limit, "offset": offset}
            )

            rows = result.fetchall()

            return [
                HistoryItem(
                    id=r[0],
                    source=r[1],
                    is_dirty=bool(r[2]),
                    confidence=r[3],
                    notes=r[4],
                    created_at=(
                        r[5].isoformat()
                        if r[5]
                        else None
                    ),
                )
                for r in rows
            ]

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("get_history failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}/image")
def get_image(event_id: int):
    _require_db()

    try:
        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT image_data FROM floor_events WHERE id = :event_id"),
                {"event_id": event_id}
            )
            row = result.fetchone()

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
