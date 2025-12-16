# FloorEye ML Service

Standalone ML inference service for YOLOv8-based dirty floor detection.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/health
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `MODEL_PATH`: Path to YOLOv8 model file (default: `models/yolov8n.pt`)
- `CONF_THRESHOLD`: Detection confidence threshold (default: `0.25`)

## API Endpoints

### `GET /health`
Health check endpoint.

### `POST /detect` or `POST /detect-image`
Detect dirty floor from uploaded image.

**Request**: Multipart form data with `image` file

**Response**:
```json
{
  "is_dirty": true,
  "confidence": 0.87,
  "conf_threshold": 0.25
}
```

## HuggingFace Spaces Deployment

1. Create new Space on HuggingFace
2. Select "Docker" SDK
3. Upload all files from `ml_service/`
4. Add Dockerfile:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

5. Set `MODEL_PATH` secret if using custom model
6. Deploy!
