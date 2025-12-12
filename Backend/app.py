from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import threading

# Routers
from routes.email_routes import router as email_router
from routes.detection_routes import router as detect_router
from routes.history_routes import router as history_router
from routes.camera_routes import router as camera_router

# Services
from backend.services.monitor_service import monitor_loop

# Database
from backend.store.db import get_connection


# =========================
# App Lifespan (Background Task)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start background monitoring thread when app starts
    and stop it gracefully when app shuts down.
    """
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_loop,
        args=(stop_event,),
        daemon=True
    )
    monitor_thread.start()

    yield  # app is running

    stop_event.set()
    monitor_thread.join()


# =========================
# FastAPI App Initialization
# =========================
app = FastAPI(
    title="FloorEye Backend Service",
    version="2.1",
    lifespan=lifespan
)

# =========================
# CORS Configuration
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # frontend access
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API Routers
# =========================
app.include_router(
    email_router,
    prefix="/email-recipients",
    tags=["Email Notification"]
)

app.include_router(
    detect_router,
    prefix="/detect",
    tags=["Detection Trigger"]
)

app.include_router(
    history_router,
    prefix="/history",
    tags=["Detection History"]
)

app.include_router(
    camera_router,
    prefix="/cameras",
    tags=["Camera Management"]
)


# =========================
# Root & Health Check
# =========================
@app.get("/")
def root():
    return {
        "service": "FloorEye Backend",
        "status": "running",
        "version": "2.1"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# =========================
# Convenience Image Endpoint
# =========================
@app.get("/image/{event_id}")
def get_image_by_event_id(event_id: int):
    """
    GET /image/{event_id}
    Fetch image binary from database by event ID.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT image_data FROM floor_events WHERE id = %s",
            (event_id,)
        )
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row or not row[0]:
            return {"error": "Image not found"}

        return Response(
            content=row[0],
            media_type="image/jpeg"
        )

    except Exception as e:
        print(f"[ERROR] get_image_by_event_id: {e}")
        return {"error": str(e)}
