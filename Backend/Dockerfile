# Railway-optimized Dockerfile for FloorEye Backend
# Target: < 2GB image size for free tier (4GB limit)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# No system dependencies needed - lightweight API only

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with no cache
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code only
COPY app/ ./app/
COPY Procfile .

# Expose port (Railway injects $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/health', timeout=5)"

# Start with uvicorn, Railway provides $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
