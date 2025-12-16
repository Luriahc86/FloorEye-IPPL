# FloorEye Quick Reference

## 🎯 System Overview

```
Browser → Railway Backend → HuggingFace ML → Response
(Camera)   (Lightweight)     (YOLO Inference)
```

---

## 📦 What Goes Where?

### Railway Backend (d:/IPPL/FloorEye/Backend)
**Allowed:**
- ✅ fastapi, uvicorn
- ✅ mysql-connector-python
- ✅ requests (HTTP client)
- ✅ python-multipart
- ✅ Business logic
- ✅ Database operations
- ✅ Email notifications

**FORBIDDEN:**
- ❌ opencv-python
- ❌ ultralytics (YOLO)
- ❌ torch, tensorflow
- ❌ Model files (.pt)
- ❌ ML inference code

---

### HuggingFace ML Service (d:/IPPL/FloorEye/ml_service)
**Allowed:**
- ✅ ultralytics (YOLO)
- ✅ opencv-python-headless
- ✅ torch (auto-installed)
- ✅ numpy
- ✅ Model files (best.pt)
- ✅ ML inference code

**FORBIDDEN:**
- ❌ Database logic
- ❌ Email service
- ❌ Business rules
- ❌ Complex routing

---

## 🔗 API Integration

### Backend → ML Service

**Endpoint:** `POST {YOLO_SERVICE_URL}`

**Request:**
```json
{
  "image": "base64_encoded_jpeg_without_prefix"
}
```

**Response:**
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
      "bbox": [x1, y1, x2, y2]
    }
  ]
}
```

---

## 🌐 Environment Variables

### Railway Backend
```bash
# Database
DB_HOST=your-mysql-host
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=flooreye

# ML Service (REQUIRED!)
YOLO_SERVICE_URL=https://your-space.hf.space/detect-frame

# Features
ENABLE_MONITOR=0  # Keep as 0!

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### HuggingFace ML Service
```bash
MODEL_PATH=models/best.pt  # Optional
CONF_THRESHOLD=0.25        # Optional
```

---

## 🚀 Quick Deploy

### 1. Deploy ML Service (HuggingFace)
```bash
cd ml_service
# Upload to HuggingFace Space (Docker SDK)
# Get URL: https://your-username-flooreye-ml.hf.space
```

### 2. Deploy Backend (Railway)
```bash
cd Backend
# Set YOLO_SERVICE_URL in Railway dashboard
# Deploy from GitHub
```

### 3. Deploy Frontend (Vercel)
```bash
cd Frontend
vercel --prod
```

---

## 🔍 Validation

### Check Backend is Clean
```bash
cd Backend
python validate_separation.py
```

### Test ML Service
```bash
curl https://your-space.hf.space/health
```

### Test Backend
```bash
curl https://your-railway.app/health
```

---

## 🐛 Troubleshooting

### Backend Error: "ModuleNotFoundError: No module named 'cv2'"
**Fix:** ❌ DO NOT add opencv to requirements.txt!  
Check for accidental `import cv2` in code.

### Backend Error: "ML service unavailable"
**Fix:** Verify YOLO_SERVICE_URL is correct and Space is running.

### ML Service Error: "Model not found"
**Fix:** Upload model file or let ultralytics auto-download.

---

## 📏 File Size Limits

| Location | Size Limit | Your Image |
|----------|-----------|------------|
| Railway Backend | ~2GB (free tier) | ~500MB ✅ |
| HuggingFace ML | No practical limit | ~4GB ✅ |

---

## ❗ Remember

**Railway handles logic, HuggingFace handles ML**

- Backend = API + Database + Email
- ML Service = YOLO + Inference + Model

**Never mix them!**
