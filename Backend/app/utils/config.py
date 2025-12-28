"""Configuration loader for FloorEye Backend."""
import os
from typing import Optional


def get_env(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with optional default."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# Database Configuration (Optional - gracefully degrades if missing)
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")

# Feature toggles
ENABLE_MONITOR = os.getenv("ENABLE_MONITOR", "0").lower() in {"1", "true", "yes", "on"}
ENABLE_DB = bool(DB_HOST and DB_USER and DB_NAME)

# YOLO Service URL (HuggingFace ML Service)
YOLO_SERVICE_URL = os.getenv("YOLO_SERVICE_URL")

# Monitoring Settings
NOTIFY_INTERVAL = int(os.getenv("NOTIFY_INTERVAL", "60"))

# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")

# Detection confidence threshold
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))
