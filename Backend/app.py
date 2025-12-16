from fastapi import FastAPI
<<<<<<< HEAD
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import threading

# Routers
from routes.email_routes import router as email_router
from routes.detection_routes import router as detect_router
from routes.history_routes import router as history_router
from routes.camera_routes import router as camera_router

# Services
from services.monitor_service import monitor_loop

# Database
from store.db import get_connection

# =========================
# App Lifespan (Background Task)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start background monitoring thread when app starts
    and stop it gracefully when app shuts down.
    """
    enable_monitor = os.getenv("ENABLE_MONITOR", "0").lower() in {"1", "true", "yes", "on"}
    stop_event = None
    monitor_thread = None

    if enable_monitor:
        stop_event = threading.Event()
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(stop_event,),
            daemon=True
        )
        monitor_thread.start()
=======
from fastapi.middleware.cors import CORSMiddleware

from routes.detection_routes import router as detect_router
from routes.history_routes import router as history_router
from routes.email_routes import router as email_router

app = FastAPI(title="FloorEye Live Camera Backend")
>>>>>>> dev

    yield  # app is running

    if stop_event is not None:
        stop_event.set()
    if monitor_thread is not None:
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

<<<<<<< HEAD
=======
app.include_router(detect_router, prefix="/detect", tags=["Detection"])

app.include_router(history_router, prefix="/history", tags=["History"])

app.include_router(email_router, prefix="/email-recipients", tags=["Email"])
>>>>>>> dev

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
<<<<<<< HEAD
    return {
        "service": "FloorEye Backend",
        "status": "running",
        "version": "2.1"
    }

=======
    return {"msg": "FloorEye Backend OK ", "mode": "live-camera"}
>>>>>>> dev

@app.get("/health")
def health():
    return {"status": "healthy"}
<<<<<<< HEAD


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
=======
>>>>>>> dev
