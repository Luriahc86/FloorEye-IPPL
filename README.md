# FloorEye - Multi-Platform Floor Detection System

YOLOv8-powered dirty floor detection system with FastAPI backend, ML inference service, and React frontend. Deployable to Railway (backend), HuggingFace Spaces (ML service), and Vercel (frontend).

## Project Structure

```
FloorEye/
├── backend/              # FastAPI backend (Railway)
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── routes/      # API routes
│   │   ├── services/    # Business logic
│   │   ├── store/       # Database layer
│   │   └── utils/       # Config & logging
│   ├── requirements.txt
│   ├── Procfile         # Railway deployment
│   └── .env.example
│
├── ml_service/          # ML inference service (HuggingFace)
│   ├── app.py          # FastAPI ML app
│   ├── detector.py     # YOLO inference
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/            # React frontend (Vercel)
│   ├── src/
│   ├── package.json
│   └── .env.example
│
└── README.md
```

## Quick Start

### Backend (Local)

```bash
cd backend
pip install -r requirements.txt

# Set environment variables (copy .env.example to .env)
export DB_HOST=your-mysql-host
export DB_USER=your-db-user
export DB_PASSWORD=your-db-password
export DB_NAME=flooreye

# Run
uvicorn app.main:app --reload
```

### ML Service (Local)

```bash
cd ml_service
pip install -r requirements.txt

# Place your YOLO model at models/yolov8n.pt
# Set MODEL_PATH in .env if different

# Run
uvicorn app:app --port 8001
```

### Frontend (Local)

```bash
cd frontend
npm install

# Create .env.local from .env.example
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Run
npm run dev
```

## Deployment

### Railway (Backend)

1. Create new Railway project
2. Connect GitHub repo
3. Select `backend/` as root directory
4. Set environment variables:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - `ML_URL` (URL to ML service)
   - `ENABLE_MONITOR=1` (optional, for camera monitoring)
5. Deploy!

Procfile automatically sets: `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

### HuggingFace Spaces (ML Service)

1. Create new Space (Docker SDK)
2. Upload files from `ml_service/`
3. Add Dockerfile:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

4. Upload your YOLO model to `models/` directory
5. Deploy!

### Vercel (Frontend)

1. Import GitHub repo to Vercel
2. Set root directory to `frontend/`
3. Framework preset: Vite
4. Environment variable: `VITE_API_BASE_URL=https://your-backend.railway.app`
5. Deploy!

## Environment Variables

### Backend

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database config (optional)
- `ML_URL` - ML service URL (default: `http://ml:8000/detect`)
- `MODEL_PATH` - Local YOLO model path (for local inference)
- `ENABLE_MONITOR` - Enable background camera monitoring (0/1)
- `CONF_THRESHOLD` - Detection confidence threshold (default: 0.25)

### ML Service

- `MODEL_PATH` - YOLO model path (default: `models/yolov8n.pt`)
- `CONF_THRESHOLD` - Detection confidence threshold (default: 0.25)

### Frontend

- `VITE_API_BASE_URL` - Backend API URL (default: `http://localhost:8000`)

## API Endpoints

### Backend

- `GET /health` - Health check
- `POST /detect/image` - Detect from image upload
- `POST /detect/frame` - Detect from base64 frame
- `GET /history` - Get detection history
- `GET /cameras` - List cameras
- `GET /email-recipients` - List email recipients

### ML Service

- `GET /health` - Health check
- `POST /detect` or `/detect-image` - Detect from image upload

## Features

- ✅ YOLOv8-based dirty floor detection
- ✅ Real-time webcam detection (frontend)
- ✅ RTSP camera monitoring (backend)
- ✅ Email alerts
- ✅ Detection history with image storage
- ✅ DB-optional mode (backend works without database)
- ✅ In-memory processing (no disk writes in production)
- ✅ Graceful error handling (monitor never crashes server)

## License

MIT
