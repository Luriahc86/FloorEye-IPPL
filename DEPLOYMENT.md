# FloorEye Deployment Guide

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│ FRONTEND (Vercel/Netlify)                       │
│ - React/TypeScript application                  │
│ - Live camera capture via getUserMedia()        │
└────────┬────────────────────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌────────────────────┐          ┌─────────────────────────┐
│ BACKEND (Railway)  │          │ ML SERVICE (HuggingFace)│
│ - Lightweight API  │─────────▶│ - YOLO inference        │
│ - MySQL database   │          │ - Heavy ML dependencies │
│ - Email service    │          │ - Model files           │
└────────────────────┘          └─────────────────────────┘
```

---

## 📦 Part 1: Deploy HuggingFace ML Service

### Prerequisites
- HuggingFace account (free)
- Trained YOLOv8 model (best.pt)

### Step 1: Create HuggingFace Space

1. Go to https://huggingface.co/new-space
2. Fill in details:
   - **Space name**: `flooreye-ml` (or your choice)
   - **License**: MIT
   - **Space SDK**: **Docker**
   - **Space hardware**: CPU Basic (free tier)

3. Click **Create Space**

### Step 2: Upload ML Service Files

Upload these files from `ml_service/` to your Space repository:

```
.
├── Dockerfile
├── main.py
├── detector.py
├── requirements.txt
└── README.md
```

**Option A: Via Web UI**
- Drag and drop files in HuggingFace UI
- Commit changes

**Option B: Via Git**
```bash
cd ml_service
git clone https://huggingface.co/spaces/YOUR-USERNAME/flooreye-ml
cp Dockerfile main.py detector.py requirements.txt README.md flooreye-ml/
cd flooreye-ml
git add .
git commit -m "Initial ML service deployment"
git push
```

### Step 3: Upload YOLO Model (Optional)

If using custom trained model:

1. In HuggingFace Space, create folder `models/`
2. Upload your `best.pt` file to `models/best.pt`
3. Set environment variable in Space settings:
   ```
   MODEL_PATH=models/best.pt
   ```

If using default YOLOv8:
- Skip this step
- Model will auto-download on first inference

### Step 4: Wait for Build

- HuggingFace will automatically build Docker image
- Check **Build Logs** tab for progress
- Wait ~5-10 minutes for first build

### Step 5: Test ML Service

Once deployed, test the endpoint:

```bash
# Get your Space URL
SPACE_URL="https://YOUR-USERNAME-flooreye-ml.hf.space"

# Test health endpoint
curl $SPACE_URL/health

# Test detection with base64 image
curl -X POST $SPACE_URL/detect-frame \
  -H "Content-Type: application/json" \
  -d '{"image": "PASTE_BASE64_HERE"}'
```

Expected response:
```json
{
  "status": "CLEAN",
  "is_dirty": false,
  "max_confidence": 0.0,
  "detections": []
}
```

✅ **Copy your Space URL** - you'll need it for the backend!

---

## 🚂 Part 2: Deploy Railway Backend

### Prerequisites
- Railway account (free tier available)
- MySQL database (Railway MySQL addon or external)

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Connect your FloorEye repository
5. Select **Backend** directory as root

### Step 2: Add MySQL Database

**Option A: Railway MySQL Plugin**
```
1. Click "New" in your project
2. Select "Database" → "Add MySQL"
3. Railway auto-provisions database
4. Connection details appear in Variables tab
```

**Option B: External MySQL**
```
Skip this step, use your existing MySQL credentials
```

### Step 3: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Database (from Railway MySQL plugin or external)
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=flooreye

# ML Service (CRITICAL - use your HuggingFace Space URL)
YOLO_SERVICE_URL=https://YOUR-USERNAME-flooreye-ml.hf.space/detect-frame

# Email (optional but recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Feature Toggles
ENABLE_MONITOR=0
CONF_THRESHOLD=0.25
NOTIFY_INTERVAL=60
```

⚠️ **IMPORTANT**: 
- Set `ENABLE_MONITOR=0` (RTSP monitoring requires opencv)
- Use your actual HuggingFace Space URL for `YOLO_SERVICE_URL`

### Step 4: Deploy

Railway auto-deploys on push to main branch.

**Manual deploy:**
```bash
cd Backend
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

Railway will:
1. Build Docker image from `Dockerfile`
2. Install lightweight dependencies (~500MB image)
3. Deploy on free tier

### Step 5: Initialize Database

Once deployed, run database schema:

```bash
# Connect to Railway MySQL
railway connect mysql

# Run schema (create tables)
CREATE TABLE IF NOT EXISTS floor_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(50),
  is_dirty BOOLEAN,
  confidence FLOAT,
  image_data LONGBLOB,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cameras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100),
  link VARCHAR(500),
  aktif BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS email_recipients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  active BOOLEAN DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 6: Test Backend

Get your Railway URL (e.g., `https://flooreye-backend.railway.app`)

```bash
# Test health endpoint
curl https://your-railway-url.railway.app/health

# Test detection endpoint
curl -X POST https://your-railway-url.railway.app/detect/frame \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "data:image/jpeg;base64,PASTE_BASE64_HERE"}'
```

---

## 🌐 Part 3: Deploy Frontend

### Prerequisites
- Vercel/Netlify account (free)

### Step 1: Update Frontend Config

Update API endpoints in frontend code to point to your Railway backend:

```typescript
// Frontend/src/config/api.ts (or wherever API base URL is defined)
export const API_BASE_URL = "https://your-railway-url.railway.app";
```

### Step 2: Deploy to Vercel

```bash
cd Frontend
npm install -g vercel
vercel login
vercel --prod
```

Or connect GitHub repo in Vercel dashboard.

### Step 3: Configure Environment Variables (if needed)

In Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
```

---

## ✅ Verification Checklist

### ML Service (HuggingFace)
- [ ] Space is public and accessible
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/detect-frame` accepts base64 JSON
- [ ] YOLO model loads without errors
- [ ] Inference completes in < 5 seconds

### Backend (Railway)
- [ ] Service is deployed and running
- [ ] Environment variables configured
- [ ] MySQL connection successful
- [ ] `/health` endpoint works
- [ ] `/detect/frame` forwards to ML service
- [ ] No opencv import errors in logs
- [ ] Docker image size < 1GB

### Frontend (Vercel/Netlify)
- [ ] Site loads without errors
- [ ] Camera permission prompt appears
- [ ] Frames sent to backend successfully
- [ ] Detection results displayed
- [ ] History page loads data from backend

---

## 🐛 Troubleshooting

### Backend Can't Reach ML Service

**Error**: `ML service unavailable: Connection timeout`

**Fix**:
1. Verify `YOLO_SERVICE_URL` is correct
2. Check HuggingFace Space is running (not sleeping)
3. Test ML service health: `curl https://your-space.hf.space/health`

### Database Connection Failed

**Error**: `mysql.connector.errors.DatabaseError`

**Fix**:
1. Verify Railway MySQL plugin is provisioned
2. Check environment variables match MySQL credentials
3. Ensure Railway DB is not paused (free tier limitation)

### OpenCV Import Error

**Error**: `ModuleNotFoundError: No module named 'cv2'`

**Fix**:
- ❌ **DO NOT** add opencv to backend requirements.txt
- ✅ This error should NOT occur if refactoring was done correctly
- Check that no code in `Backend/app/` imports `cv2`

```bash
# Verify no opencv imports
grep -r "import cv2" Backend/app/
# Should return nothing
```

### Railway Docker Build Failed

**Error**: Image size exceeds limits

**Fix**:
- Verify `requirements.txt` has NO opencv, ultralytics, numpy
- Check Dockerfile has NO opencv system dependencies
- Image should be ~500MB, not 3GB+

### Email Notifications Not Sending

**Error**: `SMTPAuthenticationError`

**Fix**:
1. Use Gmail App Password (not regular password)
2. Verify `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` are correct
3. Check Gmail "Less secure app access" settings

---

## 📊 Cost Breakdown

| Service | Tier | Cost | Limits |
|---------|------|------|--------|
| **HuggingFace Spaces** | CPU Basic | Free | Sleeps after inactivity |
| **Railway** | Hobby (Free) | $0 | $5 credit/month, 500 hours |
| **Vercel** | Hobby | Free | 100GB bandwidth |
| **MySQL** | Railway Plugin | Free* | Limited storage |

**Total**: **$0/month** for low-traffic usage

*Railway free tier provides $5/month credit, sufficient for small-scale use.

---

## 🚀 Production Recommendations

### HuggingFace
- ✅ Upgrade to **Persistent** hardware to prevent sleep ($9/month)
- ✅ Use custom domain for branding

### Railway
- ✅ Add monitoring with Railway's built-in logs
- ✅ Set up auto-scaling if traffic increases
- ✅ Use Railway's backup feature for MySQL

### General
- ✅ Set up CDN (Cloudflare) for frontend
- ✅ Enable HTTPS everywhere (free with Vercel/Railway)
- ✅ Configure CORS properly in backend
- ✅ Add rate limiting to prevent abuse
- ✅ Monitor API usage and costs

---

## 📞 Support

- Backend issues: Check `Backend/ARCHITECTURE.md`
- ML service issues: Check `ml_service/README.md`
- System architecture: Check `SYSTEM_ARCHITECTURE.md`

---

**Deployment complete! 🎉**

Railway handles logic, HuggingFace handles ML.
