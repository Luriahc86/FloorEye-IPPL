"""FloorEye Backend - Main FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import threading
import logging

from app.utils.config import ENABLE_MONITOR, ENABLE_DB
from app.utils.logging import setup_logging
from app.routes import health, detection, history, email_recipients

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App lifespan context manager.
    
    Starts background monitoring thread when app starts (if enabled),
    and stops it gracefully on shutdown.
    """
    stop_event = None
    monitor_thread = None
    
    if ENABLE_MONITOR and ENABLE_DB:
        logger.info("Starting background monitor thread")
        from app.services.monitor import monitor_loop
        
        stop_event = threading.Event()
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(stop_event,),
            daemon=True
        )
        monitor_thread.start()
    elif ENABLE_MONITOR and not ENABLE_DB:
        logger.warning("Monitor enabled but DB not configured - monitor will not start")
    
    yield  # App is running
    
    # Shutdown: stop monitor thread
    if stop_event is not None:
        logger.info("Stopping background monitor thread")
        stop_event.set()
    if monitor_thread is not None:
        monitor_thread.join(timeout=5)


# Create FastAPI app
app = FastAPI(
    title="FloorEye Backend Service",
    version="2.1",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    detection.router,
    prefix="/detect",
    tags=["Detection"]
)

app.include_router(
    history.router,
    prefix="/history",
    tags=["History"]
)

app.include_router(
    email_recipients.router,
    prefix="/email-recipients",
    tags=["Email Recipients"]
)

app.include_router(
    cameras.router,
    prefix="/cameras",
    tags=["Cameras"]
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "FloorEye Backend",
        "status": "running",
        "version": "2.1",
        "db_enabled": ENABLE_DB,
        "monitor_enabled": ENABLE_MONITOR,
    }


@app.get("/image/{event_id}")
def get_image_by_event_id(event_id: int):
    """
    GET /image/{event_id}
    Fetch image binary from database by event ID.
    Convenience endpoint (legacy support).
    """
    if not ENABLE_DB:
        return {"error": "Database not configured"}
    
    try:
        from app.store.db import get_connection
        
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
        logger.error(f"get_image_by_event_id error: {e}")
        return {"error": str(e)}
