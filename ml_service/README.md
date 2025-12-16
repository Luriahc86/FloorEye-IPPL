# FloorEye ML Service

Live camera frame inference service for dirty floor detection using YOLOv8.

## 🎯 Purpose

This service provides real-time YOLO inference for **live camera frames only**.

**Important**: This service does NOT support:
- ❌ Image file uploads
- ❌ Webcam access
- ❌ Disk storage

It ONLY accepts **base64-encoded frames** from frontend cameras.

## 🚀 Quick Start (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn main:app --reload --port 7860
```

Service runs at `http://localhost:7860`

## 📡 API Endpoints

### `GET /`
Root endpoint with service info

### `GET /health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "ml",
  "mode": "live_camera"
}
```

### `POST /detect-frame`
Detect dirty floor from live camera frame

**Request:**
```json
{
  "image": "<base64-encoded-jpeg-image>"
}
```

**Response:**
```json
{
  "status": "CLEAN" | "DIRTY",
  "is_dirty": true,
  "max_confidence": 0.87,
  "detections": [
    {
      "class_id": 0,
      "class_name": "dirty",
      "confidence": 0.87,
      "bbox": [120.5, 200.3, 450.2, 380.7]
    }
  ]
}
```

## 🌐 Deploy to HuggingFace Spaces

1. **Create new Space**
   - Space type: **Docker**
   - Space hardware: **CPU Basic** (free)

2. **Upload files**
   ```
   ml_service/
   ├── Dockerfile
   ├── main.py
   ├── detector.py
   ├── requirements.txt
   └── README.md
   ```

3. **Set Secrets (optional)**
   - `MODEL_PATH`: Custom YOLO model path (default: yolov8n.pt)
   - `CONF_THRESHOLD`: Detection threshold (default: 0.25)

4. **Deploy**
   - HuggingFace auto-builds from Dockerfile
   - Service runs on port 7860
   - Access at: `https://your-username-space-name.hf.space`

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `yolov8n.pt` | YOLO model path (auto-downloads) |
| `CONF_THRESHOLD` | `0.25` | Detection confidence threshold |
| `PORT` | `7860` | Server port (HuggingFace default) |

## 🧠 YOLO Model

- Default model: `yolov8n.pt` (auto-downloaded by ultralytics)
- Custom model: Set `MODEL_PATH` environment variable
- **DO NOT** bundle .pt files in Docker image (bloats size)

## 📝 Example Usage (JavaScript)

```javascript
// Capture frame from <video> element
const video = document.querySelector('video');
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
const ctx = canvas.getContext('2d');
ctx.drawImage(video, 0, 0);

// Convert to base64
const base64Image = canvas.toDataURL('image/jpeg', 0.95).split(',')[1];

// Send to ML service
const response = await fetch('https://your-space.hf.space/detect-frame', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ image: base64Image })
});

const result = await response.json();
console.log(result.status); // "CLEAN" or "DIRTY"
```

## 🏗️ Architecture

```
Frontend (Browser Camera)
    ↓ base64 frame
ML Service (HuggingFace)
    ↓ decode → numpy
YOLO Model
    ↓ inference
JSON Result → Frontend
```

## 📦 Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Ultralytics: YOLOv8 inference
- OpenCV (headless): Image processing
- NumPy: Array operations
- Pydantic: Request/response validation

## ⚡ Performance

- **Inference time**: ~50-200ms (CPU)
- **Image size**: Max 5MB recommended
- **Input format**: JPEG base64
- **Output**: JSON only

## 🐛 Troubleshooting

**Issue**: "Invalid image data"
- **Fix**: Ensure base64 is valid JPEG
- Remove `data:image/jpeg;base64,` prefix if present

**Issue**: "Model not found"
- **Fix**: Set `MODEL_PATH` to valid model or let ultralytics auto-download

**Issue**: "Out of memory"
- **Fix**: Reduce image resolution before encoding to base64

## 📄 License

MIT
