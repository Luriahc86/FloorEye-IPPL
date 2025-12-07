from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import threading

from routes.email_routes import router as email_router
from routes.detection_routes import router as detect_router
from routes.history_routes import router as history_router
from routes.camera_routes import router as camera_router
from services.monitor_service import monitor_loop
from store.db import get_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = threading.Event()
    t = threading.Thread(target=monitor_loop, args=(stop,), daemon=True)
    t.start()
    yield
    stop.set()
    t.join()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router, prefix="/email-recipients", tags=["Email"])
app.include_router(detect_router, prefix="/detect", tags=["Detection"])
app.include_router(history_router, prefix="/history", tags=["History"])
app.include_router(camera_router, prefix="/cameras", tags=["Cameras"])

@app.get("/")
def root():
    return {"msg": "FloorEye Backend OK 🚀", "version": "2.1"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/image/{event_id}")
def get_image_convenience(event_id: int):
    """Convenience endpoint: GET /image/{id} → fetch image data from database."""
    try:
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
    except Exception as e:
        print(f"[ERROR] get_image: {e}")
        return {"error": str(e)}