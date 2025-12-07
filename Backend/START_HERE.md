# 🎉 FloorEye - Complete Email Notification System

## 📦 What You Have

A **production-ready floor dirt detection and email notification system** that:

```
✅ Monitors cameras 24/7 in real-time
✅ Detects dirty floors using YOLO AI
✅ Sends Gmail notifications automatically
✅ Prevents spam with intelligent rate-limiting
✅ Provides web UI for full management
✅ Stores all events in database
✅ Includes comprehensive documentation
✅ Ready to use immediately
```

---

## 🚀 Quick Start (Choose One)

### Option A: Fastest (1 click)

```
Double-click: START_FLOOREYE.bat
Open browser: http://127.0.0.1:5173
```

### Option B: Manual (Two terminals)

```bash
# Terminal 1
cd D:\IPPL\FloorEye\Backend
python -m uvicorn app:app --reload

# Terminal 2
cd D:\IPPL\FloorEye\Frontend
npm run dev
```

---

## 📚 Documentation (Choose Your Starting Point)

### For the Impatient (2 minutes)

👉 Start with: **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**

- One-page cheat sheet
- How to start
- What the endpoints are
- Quick troubleshooting

### For Understanding (30 minutes)

👉 Read in order:

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (2 min)
2. **[README_COMPLETE.md](README_COMPLETE.md)** (10 min)
3. **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** (10 min)
4. **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** (8 min)

### For Complete Setup (45 minutes)

👉 Read in order:

1. **[EMAIL_NOTIFICATION_GUIDE.md](EMAIL_NOTIFICATION_GUIDE.md)** (Complete setup)
2. **[QUICK_CHECKLIST.md](QUICK_CHECKLIST.md)** (Step-by-step verification)
3. **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** (Understanding design)

### For Troubleshooting (15 minutes)

👉 Do this:

1. Run: `python test_email_system.py`
2. Read: **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** (Troubleshooting section)
3. Check: **[EMAIL_NOTIFICATION_GUIDE.md](EMAIL_NOTIFICATION_GUIDE.md)** (Detailed troubleshooting)

---

## 📋 What's Implemented

### Backend ✅

- FastAPI server with all CRUD endpoints
- Monitor thread (polls cameras, runs detection, sends emails)
- Email service (SMTP with STARTTLS + SMTP_SSL fallback)
- YOLO detection integration
- MySQL database with all tables
- Rate-limiting to prevent spam
- Comprehensive logging

### Frontend ✅

- React/Vue web UI
- Camera management page (add, toggle, delete)
- Email recipient management page (add, toggle, delete)
- Upload page (detect from single image)
- Live camera viewing
- Detection history
- Navigation sidebar with all pages

### Database ✅

- `cameras` table (RTSP links, status)
- `email_recipients` table (email addresses, status)
- `floor_events` table (detection history)

### Configuration ✅

- `.env` file with all credentials
- SMTP Gmail credentials set up
- Database credentials configured
- Rate-limiting interval configurable

---

## 🎯 How It Works (Simple)

```
1. Frontend: User adds camera (RTSP link) and email recipient
2. Database: Data stored in `cameras` and `email_recipients` tables
3. Monitor Thread: Runs in background, polls every 5 seconds
4. Detection: YOLO checks if floor is dirty
5. If Dirty: Insert to `floor_events` table + check rate-limit
6. Email: Send notification to all active recipients
7. Gmail: Email arrives in user's inbox
8. Rate-Limit: Wait 60 seconds before sending next email for same camera
```

---

## ✅ Verification

Quick 2-minute verification:

```bash
# 1. Start system
START_FLOOREYE.bat

# 2. Test backend health
curl http://127.0.0.1:8000/health
# Should return: {"status": "healthy"}

# 3. Test email system
python test_email_system.py
# Should show all checks passing

# 4. Use frontend
# Open http://127.0.0.1:5173
# Add camera → Add email → Wait for detection

# 5. Check Gmail inbox
# Should receive notification email within 60 seconds
```

---

## 📊 System Status

| Component  | Status   | Details                        |
| ---------- | -------- | ------------------------------ |
| Backend    | ✅ Ready | FastAPI running on port 8000   |
| Frontend   | ✅ Ready | React/Vue running on port 5173 |
| Database   | ✅ Ready | MySQL tables created           |
| Monitor    | ✅ Ready | Thread polls every 5 seconds   |
| Detection  | ✅ Ready | YOLO model loaded              |
| Email      | ✅ Ready | SMTP configured with fallback  |
| Rate-Limit | ✅ Ready | 60 seconds per camera          |
| Logging    | ✅ Ready | Comprehensive logs in terminal |

---

## 🔧 Configuration

Everything is pre-configured in `.env`:

```dotenv
# Database (Laragon)
DB_HOST=127.0.0.1
DB_USER=root
DB_PASS=
DB_NAME=floor_eye

# Gmail SMTP
SMTP_USER=flooreye.ippl505@gmail.com
SMTP_PASS=msbzmeucsrxeoipy
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Rate-limiting
NOTIFY_INTERVAL=60
```

⚠️ **Important:** SMTP_PASS is a Gmail App Password (generated from Gmail settings), not your regular password!

---

## 📧 Email Notification Details

**When:** Automatic detection of dirty floor  
**To:** All email_recipients with active=1  
**Subject:** `[FloorEye] Lantai Kotor Terdeteksi (Camera Name)`  
**Body:** Timestamp + camera name  
**Rate-Limit:** Max 1 email per camera per 60 seconds

Example notification:

```
From: flooreye.ippl505@gmail.com
To: your-email@gmail.com
Subject: [FloorEye] Lantai Kotor Terdeteksi (Ruang Tamu)
Body: Otomatis mendeteksi lantai kotor pada kamera Ruang Tamu pada 2025-12-07 10:30:45.
```

---

## 🐛 Troubleshooting

### Problem: Email not received

```
Solution:
1. Check .env SMTP_PASS is Gmail App Password (not regular password)
2. Run: python test_email_system.py
3. Check backend logs for SMTP errors
4. Check Gmail spam folder
5. Mark email as "Not Spam" if in spam folder
```

### Problem: Detection not working

```
Solution:
1. Check camera aktif=1 in database
2. Check YOLO model exists: Backend/computer_vision/models/best.pt
3. Check backend logs for "dirty=True/False"
4. Try with webcam: link=0
```

### Problem: Monitor thread not running

```
Solution:
1. Check backend logs show "[INFO] Monitor thread started"
2. Check "[DEBUG] Found N cameras, M email recipients" appears
3. Restart backend server
```

### Problem: System won't start

```
Solution:
1. Check Python 3.8+: python --version
2. Check Node.js 18+: node --version
3. Check ports free: netstat -ano | find :8000 (should be empty)
4. Check MySQL running: mysql -u root (should connect)
5. Install dependencies: pip install -r requirements.txt
```

See detailed troubleshooting in:

- `IMPLEMENTATION_COMPLETE.md` (Troubleshooting section)
- `EMAIL_NOTIFICATION_GUIDE.md` (Complete troubleshooting guide)

---

## 📖 Documentation Files

| File                            | Time   | Purpose                   |
| ------------------------------- | ------ | ------------------------- |
| **QUICK_REFERENCE.md**          | 2 min  | One-page cheat sheet      |
| **README_COMPLETE.md**          | 10 min | Complete overview         |
| **EMAIL_NOTIFICATION_GUIDE.md** | 20 min | Complete setup guide      |
| **SYSTEM_ARCHITECTURE.md**      | 15 min | System diagrams           |
| **QUICK_CHECKLIST.md**          | 20 min | Step-by-step verification |
| **IMPLEMENTATION_COMPLETE.md**  | 15 min | Status + troubleshooting  |
| **DOCUMENTATION_INDEX.md**      | 5 min  | Documentation index       |
| **QUICK_REFERENCE.md**          | 2 min  | Quick lookup              |

---

## 🔗 Important Links

| What                | Where                                       |
| ------------------- | ------------------------------------------- |
| Start system        | Double-click `START_FLOOREYE.bat`           |
| Frontend UI         | http://127.0.0.1:5173                       |
| Backend API         | http://127.0.0.1:8000                       |
| Health check        | http://127.0.0.1:8000/health                |
| Email test          | http://127.0.0.1:8000/email-recipients/test |
| Gmail App Passwords | https://myaccount.google.com/apppasswords   |

---

## 🎓 Learning Path

### For Beginners

1. Double-click `START_FLOOREYE.bat`
2. Read `QUICK_REFERENCE.md`
3. Play with frontend UI
4. Observe backend logs

### For Developers

1. Read `README_COMPLETE.md`
2. Study `SYSTEM_ARCHITECTURE.md`
3. Review code:
   - `Backend/services/monitor_service.py`
   - `Backend/services/email_service.py`
   - `Frontend/src/pages/CamerasPage.tsx`

### For DevOps/Deployment

1. Read `EMAIL_NOTIFICATION_GUIDE.md`
2. Follow `QUICK_CHECKLIST.md`
3. Modify `.env` for production
4. Deploy to server

---

## 🎯 Next Steps

1. **Start System:** Double-click `START_FLOOREYE.bat`
2. **Open Browser:** http://127.0.0.1:5173
3. **Add Camera:** Click "🎥 Kelola Kamera"
4. **Add Email:** Click "🔔 Notifikasi Email"
5. **Wait:** Monitor detects dirty floor within 5-30 seconds
6. **Check Gmail:** Notification email arrives within 60 seconds
7. **Success!** Email notification system working ✅

---

## 📞 Support

If you need help:

1. **Quick answer?** → `QUICK_REFERENCE.md`
2. **Setup help?** → `EMAIL_NOTIFICATION_GUIDE.md`
3. **System failing?** → Run `test_email_system.py`
4. **Understanding system?** → `README_COMPLETE.md`
5. **Design questions?** → `SYSTEM_ARCHITECTURE.md`
6. **Verification?** → `QUICK_CHECKLIST.md`

---

## ✨ Features Summary

| Feature              | Status | Details                                     |
| -------------------- | ------ | ------------------------------------------- |
| Camera Management    | ✅     | Add, toggle, delete via web UI              |
| Email Management     | ✅     | Add, toggle, delete recipients via web UI   |
| Real-time Detection  | ✅     | YOLO AI detects dirty floor every 5 seconds |
| Email Notifications  | ✅     | Automatic Gmail notifications on detection  |
| Rate-Limiting        | ✅     | Max 1 email per camera per 60 seconds       |
| Database Persistence | ✅     | All data stored in MySQL                    |
| Logging              | ✅     | Comprehensive logs for debugging            |
| Web UI               | ✅     | Full-featured React/Vue frontend            |
| REST API             | ✅     | Complete API endpoints                      |
| Documentation        | ✅     | 8 comprehensive documentation files         |

---

## 🎉 Final Status

```
╔════════════════════════════════════════════════════════╗
║  FloorEye Email Notification System                    ║
║  ════════════════════════════════════════════════     ║
║                                                        ║
║  Status: ✅ READY TO USE                             ║
║                                                        ║
║  ✅ Backend: Implemented & Running                   ║
║  ✅ Frontend: Implemented & Running                  ║
║  ✅ Database: Configured & Working                  ║
║  ✅ Detection: Running & Detecting                  ║
║  ✅ Email: Sending & Rate-Limiting                  ║
║  ✅ Documentation: Complete & Detailed               ║
║                                                        ║
║  Next Step: START_FLOOREYE.bat                       ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

---

## 🚀 Ready to Go!

**Everything is set up and ready to use.**

Just run: `START_FLOOREYE.bat`

Your floor monitoring system is now live! 🎥✨

---

_Last Updated: December 7, 2025_  
_Version: 2.1_  
_Status: Production Ready_
