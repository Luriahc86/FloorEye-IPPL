from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from store.db import get_connection
from fastapi.responses import Response

router = APIRouter()

class HistoryItem(BaseModel):
    id: int
    source: str
    is_dirty: bool
    confidence: Optional[float] = None
    notes: Optional[str] = None
    created_at: str

@router.get("/", response_model=List[HistoryItem])
def get_history(limit: int = 50, offset: int = 0):
    """Fetch detection history."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, source, is_dirty, confidence, notes, created_at
        FROM floor_events
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    history = []
    for r in rows:
        history.append(HistoryItem(
            id=r.get("id"),
            source=r.get("source"),
            is_dirty=bool(r.get("is_dirty")),
            confidence=r.get("confidence"),
            notes=r.get("notes"),
            created_at=str(r.get("created_at")),
        ))
    
    return history

@router.get("/{event_id}/image")
def get_image(event_id: int):
    """Get image data from database event."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_data FROM floor_events WHERE id = %s", (event_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row or not row[0]:
        return {"error": "Image not found"}
    
    image_data = row[0]
    return Response(content=image_data, media_type="image/jpeg")

