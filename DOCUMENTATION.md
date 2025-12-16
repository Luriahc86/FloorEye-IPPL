# FloorEye - Dokumentasi Lengkap

## 📋 Daftar Isi

1. [Ringkasan Proyek](#ringkasan-proyek)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Komponen Sistem](#komponen-sistem)
4. [Setup Development](#setup-development)
5. [Deployment](#deployment)
6. [API Documentation](#api-documentation)
7. [Integrasi End-to-End](#integrasi-end-to-end)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Ringkasan Proyek

**FloorEye** adalah sistem deteksi kebersihan lantai secara real-time menggunakan teknologi YOLOv8 (computer vision) yang terintegrasi dengan kamera browser.

### Fitur Utama

- ✅ **Live Camera Detection** - Deteksi real-time menggunakan kamera browser
- ✅ **Auto-Detection Mode** - Deteksi otomatis setiap interval tertentu
- ✅ **History Tracking** - Riwayat deteksi tersimpan di database
- ✅ **Email Notifications** - Notifikasi otomatis saat lantai kotor terdeteksi
- ✅ **Responsive UI** - Mendukung desktop & mobile

### Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| **Frontend** | React, TypeScript, Vite, TailwindCSS |
| **Backend** | FastAPI, Python, MySQL |
| **ML Service** | YOLOv8, OpenCV, PyTorch |
| **Deployment** | Vercel (FE), Railway (BE), HuggingFace (ML) |

---

## Arsitektur Sistem

### Prinsip Utama

**PEMISAHAN KETAT antara Backend Lightweight dan ML Service Heavy**

```
┌─────────────────────────────────────────────────────────────┐
│  BROWSER (Live Camera)                                      │
│  - getUserMedia() untuk akses kamera                        │
│  - Canvas untuk ekstraksi frame                             │
│  - Konversi ke base64 JPEG                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ POST /detect/frame
                 │ { image_base64: "..." }
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React + TypeScript)                              │
│  Platform: Vercel                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Tanggung Jawab:                                            │
│  - UI/UX                                                     │
│  - Camera capture                                            │
│  - Display hasil deteksi                                     │
│  - Routing & navigation                                      │
│                                                              │
│  Dependencies: react, axios, tailwindcss                    │
│  Build Size: ~500KB gzipped                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ POST /detect/frame
                 │ { image_base64: "..." }
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI - Lightweight)                            │
│  Platform: Railway                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Tanggung Jawab:                                            │
│  - HTTP routing                                              │
│  - Database operations                                       │
│  - Business logic                                            │
│  - Forward request ke ML service                             │
│  - Email notifications                                       │
│                                                              │
│  Dependencies:                                               │
│    ✅ fastapi, uvicorn                                      │
│    ✅ requests (HTTP client)                                │
│    ✅ mysql-connector-python                                │
│    ❌ TIDAK ADA opencv, ultralytics, torch                 │
│                                                              │
│  Docker Image: ~500MB (sangat ringan)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ POST /detect-frame
                 │ { image: "base64..." }
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  ML SERVICE (YOLOv8 Inference)                              │
│  Platform: HuggingFace Spaces                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Tanggung Jawab:                                            │
│  - Load YOLO model                                           │
│  - Image preprocessing                                       │
│  - ML inference                                              │
│  - Return detection result                                   │
│                                                              │
│  Dependencies:                                               │
│    ✅ ultralytics (YOLO)                                    │
│    ✅ opencv-python-headless                                │
│    ✅ torch (PyTorch)                                       │
│    ✅ numpy                                                 │
│                                                              │
│  Docker Image: ~4GB (heavy ML)                              │
└─────────────────────────────────────────────────────────────┘
```

### Alur Data

1. **Browser** → Ambil frame dari kamera via getUserMedia()
2. **Frontend** → Konversi frame ke base64 JPEG
3. **Frontend** → POST ke Backend `/detect/frame`
4. **Backend** → Decode base64, forward ke ML Service
5. **ML Service** → YOLO inference, return result
6. **Backend** → Simpan ke DB (opsional), kirim notifikasi
7. **Backend** → Return result ke Frontend
8. **Frontend** → Display "BERSIH" atau "KOTOR"

---

## Komponen Sistem

### 1. Frontend (React + TypeScript)

**Lokasi:** `Frontend/`

**Struktur:**
```
Frontend/
├── src/
│   ├── components/
│   │   ├── CameraViewer.tsx    # Komponen kamera utama
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   └── HistoryItem.tsx     # Item riwayat deteksi
│   ├── pages/
│   │   ├── LiveCameraPage.tsx  # Halaman live camera
│   │   ├── HistoryPage.tsx     # Halaman riwayat
│   │   └── NotificationsPage.tsx # Halaman notifikasi email
│   ├── services/
│   │   ├── detection.service.ts # API calls untuk deteksi
│   │   ├── history.service.ts   # API calls untuk history
│   │   └── email.service.ts     # API calls untuk email
│   └── App.tsx
├── package.json
└── vite.config.ts
```

**Fitur Utama:**
- Live camera capture menggunakan WebRTC
- Canvas-based frame extraction
- Auto-detection mode
- Real-time result display
- Responsive design

---

### 2. Backend (FastAPI)

**Lokasi:** `Backend/`

**Struktur:**
```
Backend/
├── app/
│   ├── routes/
│   │   ├── detection.py        # Endpoint deteksi
│   │   ├── history.py          # Endpoint riwayat
│   │   ├── email_recipients.py # Endpoint email
│   │   └── cameras.py          # Endpoint kamera
│   ├── services/
│   │   ├── emailer.py          # Service email
│   │   └── monitor.py          # Background monitor (disabled)
│   ├── store/
│   │   └── db.py               # Database connection
│   ├── utils/
│   │   ├── config.py           # Environment config
│   │   └── logging.py          # Logging setup
│   └── main.py                 # FastAPI app
├── requirements.txt            # Lightweight deps only
└── Dockerfile                  # Optimized untuk Railway
```

**Dependencies (requirements.txt):**
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.17
mysql-connector-python==9.1.0
requests==2.32.3
python-dotenv==1.0.1
email-validator==2.2.0
```

**⚠️ PENTING:** Backend TIDAK boleh mengandung:
- ❌ opencv-python
- ❌ ultralytics
- ❌ torch
- ❌ Model files (.pt)

---

### 3. ML Service (YOLOv8)

**Lokasi:** `ml_service/`

**Struktur:**
```
ml_service/
├── main.py          # FastAPI app dengan endpoint ML
├── detector.py      # YOLO inference logic
├── requirements.txt # Heavy ML dependencies
├── dockerfile       # Untuk HuggingFace Spaces
└── README.md
```

**Dependencies (requirements.txt):**
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
opencv-python-headless==4.10.0.84
ultralytics==8.3.0
numpy==1.26.4
pydantic==2.10.5
```

**API Contract:**

**Request:**
```json
POST /detect-frame
{
  "image": "base64_encoded_jpeg_without_prefix"
}
```

**Response:**
```json
{
  "status": "DIRTY" | "CLEAN",
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

---

## Setup Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- MySQL (opsional, untuk fitur history)
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd FloorEye
```

### 2. Setup Frontend

```bash
cd Frontend
npm install

# Buat file .env
cp .env.example .env

# Edit .env
# VITE_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend akan berjalan di `http://localhost:5173`

### 3. Setup Backend

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Buat file .env
cp .env.example .env

# Edit .env - minimal konfigurasi:
# YOLO_SERVICE_URL=http://localhost:7860/detect-frame
# ENABLE_MONITOR=0

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di `http://localhost:8000`

### 4. Setup ML Service

```bash
cd ml_service
pip install -r requirements.txt

# Optional: set MODEL_PATH di .env
# MODEL_PATH=models/best.pt

# Run server
uvicorn main:app --reload --port 7860
```

ML Service akan berjalan di `http://localhost:7860`

### 5. Testing

1. Buka browser: `http://localhost:5173`
2. Navigate ke "Live Camera"
3. Klik "Aktifkan Kamera"
4. Klik "Deteksi Sekarang"
5. Verifikasi hasil muncul

---

## Deployment

### Arsitektur Deployment

```
Frontend (Vercel) → Backend (Railway) → ML Service (HuggingFace)
```

### 1. Deploy ML Service ke HuggingFace

**Platform:** HuggingFace Spaces  
**Type:** Docker

**Langkah:**

1. Buat Space baru di HuggingFace
2. Pilih SDK: Docker
3. Upload files dari folder `ml_service/`:
   - `main.py`
   - `detector.py`
   - `requirements.txt`
   - `dockerfile`
   - `README.md`

4. (Opsional) Upload model YOLO:
   - Buat folder `models/`
   - Upload `best.pt`
   - Set env var: `MODEL_PATH=models/best.pt`

5. Space akan auto-build dan deploy
6. Tunggu ~5-10 menit
7. Test endpoint health: `GET /health`

**Environment Variables (HuggingFace):**
```bash
MODEL_PATH=yolov8n.pt  # atau models/best.pt untuk custom model
CONF_THRESHOLD=0.25
```

---

### 2. Deploy Backend ke Railway

**Platform:** Railway  
**Type:** Docker (from Dockerfile)

**Langkah:**

1. Buat project di Railway
2. Connect GitHub repository
3. Select folder: `Backend/`
4. Railway akan auto-detect Dockerfile

5. **Set Environment Variables:**
```bash
YOLO_SERVICE_URL=https://your-space.hf.space/detect-frame
ENABLE_MONITOR=0
CONF_THRESHOLD=0.25

# Database (optional)
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=flooreye

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
```

6. Deploy akan berjalan otomatis
7. Test endpoint: `GET /health`

**Database Setup (Optional):**

Jika menggunakan MySQL:

```sql
CREATE TABLE floor_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(50),
  is_dirty BOOLEAN,
  confidence FLOAT,
  image_data LONGBLOB,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cameras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100),
  link VARCHAR(500),
  aktif BOOLEAN DEFAULT 1
);

CREATE TABLE email_recipients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  active BOOLEAN DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3. Deploy Frontend ke Vercel

**Platform:** Vercel  
**Type:** Vite React App

**Langkah:**

1. Connect GitHub repository to Vercel
2. Select folder: `Frontend/`
3. Build command: `npm run build`
4. Output directory: `dist`

5. **Set Environment Variables:**
```bash
VITE_API_BASE_URL=https://your-backend.railway.app
```

6. Deploy
7. Test aplikasi di browser

**Redeploy:**

Setiap push ke branch `main` akan trigger auto-deploy.

---

## API Documentation

### Backend Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "running",
  "service": "FloorEye Backend",
  "version": "2.1",
  "db_enabled": true,
  "monitor_enabled": false
}
```

---

#### 2. Detect from Frame (Live Camera)

```http
POST /detect/frame
Content-Type: application/json
```

**Request:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "notes": "live-camera-auto"
}
```

**Response:**
```json
{
  "id": 123,
  "is_dirty": true,
  "confidence": 0.87,
  "created_at": "2025-12-16T13:00:00",
  "source": "camera",
  "notes": "live-camera-auto"
}
```

---

#### 3. Detect from File Upload

```http
POST /detect/image
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary image data>
```

**Response:**
```json
{
  "is_dirty": false,
  "confidence": 0.12,
  "source": "upload"
}
```

---

#### 4. Get Detection History

```http
GET /history?limit=50&offset=0
```

**Response:**
```json
{
  "total": 150,
  "events": [
    {
      "id": 123,
      "source": "camera",
      "is_dirty": true,
      "confidence": 0.87,
      "created_at": "2025-12-16T13:00:00",
      "notes": "live-camera-auto"
    }
  ]
}
```

---

#### 5. Get Email Recipients

```http
GET /email-recipients
```

**Response:**
```json
{
  "recipients": [
    {
      "id": 1,
      "email": "user@example.com",
      "active": true,
      "created_at": "2025-12-01T10:00:00"
    }
  ]
}
```

---

#### 6. Add Email Recipient

```http
POST /email-recipients
Content-Type: application/json
```

**Request:**
```json
{
  "email": "newuser@example.com"
}
```

---

### ML Service Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ml",
  "mode": "live_camera"
}
```

---

#### 2. Detect Frame

```http
POST /detect-frame
Content-Type: application/json
```

**Request:**
```json
{
  "image": "base64_encoded_jpeg"
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
      "bbox": [100.5, 200.3, 350.2, 450.8]
    }
  ]
}
```

---

## Integrasi End-to-End

### Code Implementation

#### Backend - Forward ke ML Service

**File:** `Backend/app/routes/detection.py`

```python
def call_ml_service(image_bytes: bytes):
    """
    Call HuggingFace ML service for detection.
    Sends base64-encoded image to /detect-frame endpoint.
    """
    try:
        # Encode image bytes to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Send JSON payload to ML service
        resp = requests.post(
            YOLO_SERVICE_URL,
            json={"image": image_b64},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        
        # Extract is_dirty and confidence
        return {
            "is_dirty": result.get("is_dirty", False),
            "confidence": result.get("max_confidence", 0.0)
        }
    except Exception as e:
        logger.error(f"ML service call failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML service unavailable: {e}")

@router.post("/frame")
async def detect_frame(payload: FramePayload):
    """Detect dirty floor from base64-encoded frame."""
    try:
        # Decode image
        image_bytes = decode_b64(payload.image_base64)
        
        # Call ML service
        result = call_ml_service(image_bytes)
        detected = bool(result.get("is_dirty", False))
        confidence = float(result.get("confidence", 0.0))
        
        return {
            "is_dirty": detected,
            "confidence": confidence,
            "source": "camera"
        }
    except Exception as e:
        logger.error(f"detect_frame error: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")
```

---

#### Frontend - Camera Capture

**File:** `Frontend/src/components/CameraViewer.tsx`

```typescript
// Capture frame from video element
const captureFrame = () => {
  const video = videoRef.current;
  const canvas = canvasRef.current;

  if (!video || !canvas) return "";

  canvas.width = 1280;
  canvas.height = 720;

  const ctx = canvas.getContext("2d");
  if (!ctx) return "";

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert to base64 JPEG (95% quality)
  return canvas.toDataURL("image/jpeg", 0.95);
};

// Send frame to backend
const sendToDetectAPI = async () => {
  try {
    setIsDetecting(true);
    setError(null);

    const base64 = captureFrame();

    const res = await fetch(`${API_BASE}/detect/frame`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        image_base64: base64, 
        notes: "manual-detect" 
      }),
    });

    const data: DetectionResponse = await res.json();
    setResult(data);
    onResult?.(data);
    
  } catch (err) {
    console.error(err);
    setError("Gagal mengirim frame ke backend.");
  } finally {
    setIsDetecting(false);
  }
};
```

---

### Environment Variables

#### Frontend (.env)

```bash
# Backend API URL
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

#### Backend (.env)

```bash
# ML Service URL (REQUIRED)
YOLO_SERVICE_URL=https://your-ml-space.hf.space/detect-frame

# Database (Optional)
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-user
DB_PASSWORD=your-password
DB_NAME=flooreye

# Feature Toggles
ENABLE_MONITOR=0
CONF_THRESHOLD=0.25

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

#### ML Service (.env)

```bash
# Model path (optional)
MODEL_PATH=yolov8n.pt

# Confidence threshold
CONF_THRESHOLD=0.25

# Port (HuggingFace default)
PORT=7860
```

---

## Troubleshooting

### 1. CORS Error di Frontend

**Problem:**
```
Access to fetch at '...' has been blocked by CORS policy
```

**Solution:**

Backend sudah dikonfigurasi dengan CORS:

```python
# Backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Jika masih terjadi:
1. Restart backend service
2. Clear browser cache
3. Verify backend URL benar

---

### 2. ML Service Timeout

**Problem:**
```
ML service unavailable: Connection timeout
```

**Cause:**
- HuggingFace Space sedang sleep (free tier)
- Network issue

**Solution:**
1. Buka URL ML service di browser untuk wake up
2. Tunggu 30 detik
3. Test endpoint `/health`
4. Retry detection

---

### 3. Camera Permission Denied

**Problem:**
```
Tidak dapat mengakses kamera
```

**Solution:**
1. Pastikan menggunakan HTTPS (atau localhost)
2. Check browser permissions
3. Restart browser
4. Gunakan browser lain (Chrome/Firefox recommended)

---

### 4. Backend Cannot Import cv2

**Problem:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solution:**

⚠️ JANGAN install opencv di backend!

Backend TIDAK BOLEH mengandung opencv. Check:

```bash
# Verify requirements.txt TIDAK ada opencv
grep -i opencv Backend/requirements.txt
# Harus return nothing

# Verify code TIDAK import cv2
grep -r "import cv2" Backend/app/
# Harus return nothing
```

Jika ada, hapus segera!

---

### 5. Railway Build Failed - Image Too Large

**Problem:**
```
Docker image exceeds size limit
```

**Solution:**

Verify Backend dependencies lightweight:

```bash
cd Backend
cat requirements.txt
# Harus HANYA contain:
# - fastapi
# - uvicorn
# - requests
# - mysql-connector-python
# - python-multipart
# - python-dotenv
# - email-validator

# TIDAK BOLEH ada:
# - opencv
# - ultralytics
# - torch
# - numpy (heavy)
```

Run validation:
```bash
python Backend/validate_separation.py
```

---

### 6. Environment Variable Not Found

**Problem:**
```
import.meta.env.VITE_API_BASE_URL is undefined
```

**Solution:**

1. Vercel: Add env var di dashboard dengan prefix `VITE_`
2. Railway: Add env var di Variables tab
3. Local: Copy `.env.example` ke `.env`
4. Redeploy setelah update env vars
5. Clear browser cache

---

## Best Practices

### 1. Backend Development

✅ **DO:**
- Gunakan environment variables untuk semua URLs
- Implement proper error handling
- Log semua errors
- Keep dependencies minimal
- Use type hints di Python
- Write docstrings

❌ **DON'T:**
- Install opencv atau ML libraries di backend
- Hardcode URLs
- Expose sensitive data di logs
- Run blocking operations
- Store large files locally

---

### 2. Frontend Development

✅ **DO:**
- Handle camera permissions gracefully
- Show loading states
- Implement error boundaries
- Optimize image quality vs size
- Use TypeScript strictly
- Implement responsive design

❌ **DON'T:**
- Send uncompressed images
- Block UI thread
- Ignore errors
- Hardcode API URLs

---

### 3. ML Service Development

✅ **DO:**
- Lazy-load model (on first request)
- Cache model in memory
- Return structured JSON
- Implement health checks
- Log inference times

❌ **DON'T:**
- Load model on every request
- Save files to disk
- Process multiple requests simultaneously (single-threaded inference)
- Return raw numpy arrays

---

### 4. Security

✅ **DO:**
- Use HTTPS in production
- Validate all inputs
- Sanitize user data
- Use environment variables for secrets
- Implement rate limiting
- Rotate credentials regularly

❌ **DON'T:**
- Commit `.env` files
- Expose database credentials
- Trust client-side data
- Disable CORS in production
- Log sensitive information

---

### 5. Deployment

✅ **DO:**
- Use separate environments (dev/staging/prod)
- Automate deployments
- Monitor logs
- Set up health checks
- Document environment variables
- Version your deployments

❌ **DON'T:**
- Deploy directly to production
- Skip testing
- Ignore error logs
- Deploy with hardcoded values

---

## Performance Optimization

### Frontend

- Compress images before sending (JPEG 95% quality)
- Debounce auto-detection
- Lazy load components
- Use React.memo untuk komponen heavy
- Optimize re-renders

### Backend

- Keep dependencies minimal
- Use connection pooling untuk DB
- Implement caching where appropriate
- Set appropriate timeouts
- Monitor memory usage

### ML Service

- Use model caching
- Optimize image preprocessing
- Consider GPU instance untuk production
- Monitor inference times
- Implement request queuing jika perlu

---

## Database Schema

### Table: floor_events

```sql
CREATE TABLE floor_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(50),           -- 'camera', 'upload', 'camera_{id}'
  is_dirty BOOLEAN,             -- TRUE jika kotor
  confidence FLOAT,             -- 0.0 - 1.0
  image_data LONGBLOB,          -- Gambar binary (opsional)
  notes TEXT,                   -- Catatan tambahan
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_created (created_at),
  INDEX idx_dirty (is_dirty)
);
```

### Table: cameras

```sql
CREATE TABLE cameras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100),            -- Nama kamera
  link VARCHAR(500),            -- RTSP URL
  aktif BOOLEAN DEFAULT 1,      -- Status aktif/nonaktif
  INDEX idx_aktif (aktif)
);
```

### Table: email_recipients

```sql
CREATE TABLE email_recipients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  active BOOLEAN DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_active (active)
);
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# ML Service
curl https://your-ml-service/health

# Backend
curl https://your-backend/health

# Frontend
curl https://your-frontend/
```

### Logs

**Railway (Backend):**
- View logs di Railway dashboard
- Monitor error rates
- Check response times

**HuggingFace (ML):**
- View logs di Space logs tab
- Monitor inference times
- Check for model loading errors

**Vercel (Frontend):**
- View deployment logs
- Check build status
- Monitor function invocations

---

## Scaling Considerations

### Free Tier Limits

| Platform | Limit | Current Usage |
|----------|-------|---------------|
| **Vercel** | 100GB bandwidth/month | ~1GB |
| **Railway** | $5 credit/month | ~$3 |
| **HuggingFace** | Sleeps after inactivity | N/A |

### Upgrade Paths

**Frontend (Vercel):**
- Pro plan untuk unlimited bandwidth
- CDN optimization

**Backend (Railway):**
- Hobby plan untuk lebih banyak credit
- Optimize database queries
- Add Redis caching

**ML Service (HuggingFace):**
- Upgrade ke Persistent hardware (no sleep)
- Upgrade ke GPU untuk inference lebih cepat
- Consider self-hosted dengan GPU

---

## Kesimpulan

**FloorEye** adalah sistem deteksi kebersihan lantai yang terintegrasi dengan:

✅ **Frontend (React)** - UI/UX dan camera capture  
✅ **Backend (FastAPI)** - Business logic dan routing  
✅ **ML Service (YOLO)** - Computer vision inference  

**Prinsip Utama:**
- **Separation of Concerns** - Backend lightweight, ML heavy
- **Environment Variables** - Semua URLs via env vars
- **No Hardcoding** - Flexible untuk deployment
- **Production Ready** - Error handling, logging, monitoring

**Deployment:**
- Frontend di Vercel
- Backend di Railway  
- ML Service di HuggingFace

**Status:** ✅ Production Ready

---

**Dokumentasi Lengkap - FloorEye IPPL**  
**Versi:** 2.1  
**Terakhir diupdate:** 16 Desember 2025
