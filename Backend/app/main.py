from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import threading
import logging

from app.utils.config import ENABLE_MONITOR, ENABLE_DB
from app.utils.logging import setup_logging
from app.routes import (
    health_router,
    detection_router,
    history_router,
    email_recipients_router,
    db_test_router,
)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = None
    monitor_thread = None

    if ENABLE_DB:
        try:
            from app.store.database import init_engine
            init_engine()
            logger.info("SQLAlchemy database engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")

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
        logger.warning("Monitor enabled but DB not configured")

    yield

    if stop_event:
        logger.info("Stopping background monitor thread")
        stop_event.set()
    if monitor_thread:
        monitor_thread.join(timeout=5)


app = FastAPI(
    title="FloorEye Backend Service",
    version="2.2.0",
    lifespan=lifespan,
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    tags=["Health"]
)

app.include_router(
    detection_router,
    prefix="/detect",
    tags=["Detection"]
)

app.include_router(
    history_router,
    prefix="/history",
    tags=["History"]
)

app.include_router(
    email_recipients_router,
    prefix="/email-recipients",
    tags=["Email Recipients"]
)

app.include_router(
    db_test_router,
    tags=["Database"]
)


@app.get("/")
def root():
    return {
        "service": "FloorEye Backend",
        "status": "running",
        "version": "2.2.0",
        "db_enabled": ENABLE_DB,
        "monitor_enabled": ENABLE_MONITOR,
    }


@app.get("/image/{event_id}")
def get_image_by_event_id(event_id: int):
    if not ENABLE_DB:
        return {"error": "Database not configured"}

    try:
        from sqlalchemy import text
        from app.store.db import get_db_connection

        with get_db_connection() as conn:
            result = conn.execute(
                text("SELECT image_data FROM floor_events WHERE id = :event_id"),
                {"event_id": event_id}
            )
            row = result.fetchone()

            if not row or not row[0]:
                return {"error": "Image not found"}

            return Response(
                content=row[0],
                media_type="image/jpeg"
            )

    except Exception as e:
        logger.error(f"get_image_by_event_id error: {e}")
        return {"error": str(e)}