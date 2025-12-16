# FloorEye Backend Architecture

## 🎯 Core Principle: Lightweight Railway Backend

This backend is **STRICTLY** a lightweight API layer designed for Railway's free tier.

### ⚠️ CRITICAL RULES

**Railway Backend (THIS SERVICE) MUST:**
- ✅ Handle HTTP routing (FastAPI)
- ✅ Manage database operations (MySQL)
- ✅ Implement business logic
- ✅ Forward requests to ML service
- ✅ Send email notifications
- ✅ Stay under 2GB Docker image size

**Railway Backend MUST NOT:**
- ❌ Import opencv (cv2)
- ❌ Import ultralytics (YOLO)
- ❌ Import torch/tensorflow
- ❌ Contain .pt model files
- ❌ Perform ML inference locally

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   Browser       │  Live camera capture (WebRTC/getUserMedia)
│  (Frontend)     │
└────────┬────────┘
         │ POST /detect/frame (base64 image)
         ▼
┌─────────────────────────────────────────────────┐
│  Railway Backend (THIS SERVICE)                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - FastAPI routing                              │
│  - MySQL database operations                    │
│  - Email notifications                          │
│  - Business logic                               │
│                                                  │
│  Dependencies:                                   │
│    • fastapi                                     │
│    • uvicorn                                     │
│    • mysql-connector-python                     │
│    • requests                                    │
│    • python-multipart                           │
│                                                  │
│  Image size: ~500MB (well under 2GB limit)      │
└────────┬────────────────────────────────────────┘
         │ POST $YOLO_SERVICE_URL (base64 JSON)
         │ {"image": "base64_encoded_jpeg"}
         ▼
┌─────────────────────────────────────────────────┐
│  HuggingFace ML Service                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - YOLOv8 inference                             │
│  - Model loading (best.pt)                      │
│  - Heavy ML dependencies                        │
│                                                  │
│  Dependencies:                                   │
│    • ultralytics (YOLO)                         │
│    • opencv-python-headless                     │
│    • torch                                       │
│    • numpy                                       │
│                                                  │
│  Image size: 3-5GB (no problem on HuggingFace)  │
└────────┬────────────────────────────────────────┘
         │ JSON response
         │ {"is_dirty": bool, "max_confidence": float, ...}
         ▼
┌─────────────────┐
│ Railway Backend │ Store result in DB, send email if dirty
└─────────────────┘
```

---

## 📂 Directory Structure

```
Backend/
├── app/
│   ├── routes/          # API endpoints
│   │   ├── detection.py    # ✅ Calls ML service (no local inference)
│   │   ├── history.py      # ✅ Database queries
│   │   ├── cameras.py      # ✅ Camera management
│   │   └── email_recipients.py
│   ├── services/
│   │   ├── emailer.py      # ✅ Email notifications
│   │   └── monitor.py      # ⚠️ DISABLED (needs opencv for RTSP)
│   ├── store/
│   │   └── db.py           # ✅ Database connection
│   └── utils/
│       ├── config.py       # ✅ Environment variables
│       └── logging.py      # ✅ Logging setup
├── requirements.txt        # ✅ LIGHTWEIGHT dependencies only
├── Dockerfile              # ✅ Minimal, no opencv system libs
└── .env.example            # ✅ YOLO_SERVICE_URL required
```

---

## 🔧 Configuration

### Required Environment Variables

```bash
# Database (required for full functionality)
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=flooreye

# YOLO ML Service (REQUIRED)
YOLO_SERVICE_URL=https://your-username-flooreye-ml.hf.space/detect-frame

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Feature Toggles
ENABLE_MONITOR=0          # ⚠️ Keep as 0 (RTSP monitoring requires opencv)
CONF_THRESHOLD=0.25
NOTIFY_INTERVAL=60
```

### ⚠️ MONITOR Feature Disabled

The background RTSP camera monitoring feature is **DISABLED** because:

1. **Requires opencv**: RTSP camera capture needs `cv2.VideoCapture`
2. **Violates architecture**: Railway backend must not have opencv
3. **Better alternatives**:
   - Use browser-based camera capture (recommended)
   - Deploy separate microservice for RTSP monitoring
   - Use edge devices that send frames to backend

**Set `ENABLE_MONITOR=0` in production.**

---

## 🚀 API Endpoints

### Detection Endpoints

#### `POST /detect/frame`
- **Purpose**: Detect dirty floor from browser camera frame
- **Input**: `{"image_base64": "...", "notes": "optional"}`
- **Flow**:
  1. Decode base64 image
  2. Forward to HuggingFace ML service
  3. Store result in database
  4. Send email if dirty detected
  5. Return result to frontend

#### `POST /detect/image`
- **Purpose**: Detect dirty floor from uploaded file
- **Input**: Multipart file upload
- **Flow**: Same as `/detect/frame`

### Other Endpoints

- `GET /health` - Health check
- `GET /history` - Fetch detection history
- `GET /cameras` - Manage cameras
- `GET /email-recipients` - Manage email recipients

---

## 🎨 ML Service Integration

### API Contract

**Backend → ML Service**

```http
POST https://your-space.hf.space/detect-frame
Content-Type: application/json

{
  "image": "base64_encoded_jpeg_without_prefix"
}
```

**ML Service → Backend**

```json
{
  "status": "DIRTY",
  "is_dirty": true,
  "max_confidence": 0.87,
  "detections": [
    {
      "class_id": 0,
      "class_name": "Lantai Kotor",
      "confidence": 0.87,
      "bbox": [100.5, 200.3, 350.2, 450.8]
    }
  ]
}
```

### Implementation

See `app/routes/detection.py::call_ml_service()`:

```python
def call_ml_service(image_bytes: bytes):
    # Encode to base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Send to HuggingFace
    resp = requests.post(
        YOLO_SERVICE_URL,
        json={"image": image_b64},
        timeout=30,
    )
    
    result = resp.json()
    return {
        "is_dirty": result.get("is_dirty", False),
        "confidence": result.get("max_confidence", 0.0)
    }
```

---

## 🐳 Docker Image Size

**Before refactoring (WITH opencv/YOLO)**:
- Image size: ~3.5 GB
- ❌ Exceeds Railway free tier comfort zone

**After refactoring (WITHOUT opencv/YOLO)**:
- Image size: ~500 MB
- ✅ Well within Railway limits
- ✅ Fast builds and deploys

---

## 🔍 Verification Checklist

### ✅ Backend is Lightweight

```bash
# Check requirements.txt
cat requirements.txt | grep -E "(opencv|ultralytics|torch|numpy)"
# Should return NOTHING

# Check imports
grep -r "import cv2" app/
grep -r "from ultralytics" app/
# Should return NOTHING or only in disabled code

# Check Docker image size (after build)
docker images | grep flooreye-backend
# Should be under 1GB
```

### ✅ ML Service Has Everything

```bash
cd ../ml_service
cat requirements.txt | grep -E "(opencv|ultralytics)"
# Should show opencv-python-headless and ultralytics
```

---

## 🚨 Common Mistakes to Avoid

### ❌ DO NOT add opencv back to requirements.txt

```diff
# requirements.txt
fastapi==0.115.0
- opencv-python-headless==4.10.0.84  # ❌ NO!
```

### ❌ DO NOT import cv2 in backend code

```diff
# app/routes/detection.py
- import cv2  # ❌ NO!
- import numpy as np  # ❌ NO!
```

### ❌ DO NOT perform local inference

```diff
# app/routes/detection.py
- from ultralytics import YOLO  # ❌ NO!
- model = YOLO("best.pt")  # ❌ NO!
- results = model(frame)  # ❌ NO!
```

### ✅ ALWAYS call ML service instead

```python
# ✅ YES!
result = call_ml_service(image_bytes)
```

---

## 📊 Production Deployment

### Railway Backend

1. **Set environment variables** in Railway dashboard:
   ```
   YOLO_SERVICE_URL=https://your-ml-service.hf.space/detect-frame
   DB_HOST=...
   DB_USER=...
   DB_PASSWORD=...
   ```

2. **Deploy**:
   ```bash
   git push railway main
   ```

3. **Verify**:
   - Check logs for no opencv import errors
   - Test `/health` endpoint
   - Test `/detect/frame` endpoint

### HuggingFace ML Service

See `../ml_service/README.md`

---

## 📝 Summary

| Aspect | Railway Backend | HuggingFace ML |
|--------|----------------|----------------|
| Purpose | API + Business Logic | ML Inference |
| Dependencies | fastapi, mysql | ultralytics, opencv, torch |
| Image Size | ~500MB | ~4GB |
| Imports | ❌ No cv2, YOLO | ✅ cv2, YOLO |
| Handles | DB, email, routing | YOLO detection |

**Statement**: **Railway handles logic, HuggingFace handles ML**

---

## 🔗 Related Documentation

- `../ml_service/README.md` - ML service documentation
- `../SYSTEM_ARCHITECTURE.md` - Overall system architecture
- `.env.example` - Environment variable template
