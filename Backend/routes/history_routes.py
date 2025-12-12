from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import Response

from store.db import get_connection

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
    created_at: str


# =========================
# Routes
# =========================
@router.get("/", response_model=List[HistoryItem])
def get_history(limit: int = 50, offset: int = 0):
    """Fetch detection history."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, source, is_dirty, confidence, notes, created_at
            FROM floor_events
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )

        rows = cursor.fetchall()

        history = [
            HistoryItem(
                id=r["id"],
                source=r["source"],
                is_dirty=bool(r["is_dirty"]),
                confidence=r.get("confidence"),
                notes=r.get("notes"),
                created_at=r["created_at"].isoformat()
                if r.get("created_at")
                else None,
            )
            for r in rows
        ]

        return history

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


@router.get("/{event_id}/image")
def get_image(event_id: int):
    """Get image data from database event."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT image_data FROM floor_events WHERE id = %s",
            (event_id,),
        )
        row = cursor.fetchone()

        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")

        return Response(
            content=row[0],
            media_type="image/jpeg",
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()
