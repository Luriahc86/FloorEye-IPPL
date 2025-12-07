# 📖 FloorEye Documentation Index

## 📌 Start Here

**New to FloorEye?** Start with these files in order:

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐

   - One-page cheat sheet
   - Quick start command
   - Essential endpoints
   - Troubleshooting
   - _Time: 2 minutes_

2. **[README_COMPLETE.md](README_COMPLETE.md)** ⭐⭐

   - Complete system overview
   - What's been implemented
   - How it works step-by-step
   - Technology stack
   - _Time: 10 minutes_

3. **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** ⭐⭐⭐
   - What has been implemented
   - Verification checklist
   - Troubleshooting guide
   - Next steps
   - _Time: 15 minutes_

---

## 🎯 For Specific Tasks

### Getting Started

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start in 2 minutes
- **[START_FLOOREYE.bat](START_FLOOREYE.bat)** - Double-click to start system

### Setup & Configuration

- **[EMAIL_NOTIFICATION_GUIDE.md](EMAIL_NOTIFICATION_GUIDE.md)** - Complete setup guide with all configurations
- **[QUICK_CHECKLIST.md](QUICK_CHECKLIST.md)** - Step-by-step verification checklist

### Understanding the System

- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - System diagrams, data flow, database schema
- **[README_COMPLETE.md](README_COMPLETE.md)** - Technical details and overview

### Testing & Debugging

- **[test_email_system.py](test_email_system.py)** - Python script to verify system health
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Troubleshooting guide

### API Reference

- **[EMAIL_NOTIFICATION_GUIDE.md](EMAIL_NOTIFICATION_GUIDE.md)** - API endpoint documentation in setup section
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - API endpoint list with details

---

## 📚 Complete File List

### Documentation Files (in this directory)

```
QUICK_REFERENCE.md              ← One-page cheat sheet
README_COMPLETE.md              ← Complete overview
IMPLEMENTATION_COMPLETE.md      ← What's done + verification
EMAIL_NOTIFICATION_GUIDE.md     ← Setup + troubleshooting
SYSTEM_ARCHITECTURE.md          ← Diagrams + data flow
QUICK_CHECKLIST.md              ← Step-by-step verification
START_FLOOREYE.bat              ← Windows startup script
test_email_system.py            ← System health test
DOCUMENTATION_INDEX.md          ← This file
```

### Backend Code (`Backend/`)

```
app.py                          ← Main FastAPI application
.env                            ← Configuration (SMTP, DB, etc.)
requirements.txt                ← Python dependencies

services/
  └─ email_service.py           ← SMTP email sending
  └─ monitor_service.py         ← Detection loop + notifications
  └─ detection_service.py       ← Detection helper

routes/
  └─ camera_routes.py           ← Camera CRUD endpoints
  └─ email_routes.py            ← Email recipient CRUD endpoints
  └─ detection_routes.py        ← Detection endpoints
  └─ history_routes.py          ← History endpoints

computer_vision/
  └─ detector.py                ← YOLO detection logic
  └─ models/best.pt             ← Trained YOLO model

store/
  └─ db.py                      ← Database connection
  └─ tabel.sql                  ← SQL schema
```

### Frontend Code (`Frontend/src/`)

```
pages/
  └─ CamerasPage.tsx            ← Camera management UI
  └─ NotificationsPage.tsx      ← Email management UI
  └─ UploadPage.tsx             ← Single image upload
  └─ LiveCameraPage.tsx         ← Live camera view
  └─ HistoryPage.tsx            ← Detection history

services/
  └─ camera.service.ts          ← Camera API wrapper
  └─ email.service.ts           ← Email API wrapper
  └─ detection.service.ts       ← Detection API wrapper
  └─ history.service.ts         ← History API wrapper

components/
  └─ Sidebar.tsx                ← Navigation menu

router/
  └─ index.tsx                  ← Route definitions
```

---

## 🗺️ Documentation Map

```
┌─────────────────────────────────────────────────────────────┐
│                    START HERE                                │
│              QUICK_REFERENCE.md                              │
│         (One-page cheat sheet, 2 minutes)                    │
└─────────────┬───────────────────────────────────────────────┘
              │
        ┌─────▼──────────────────────────────────┐
        │ Want to understand the system?         │
        │ → README_COMPLETE.md (10 min)          │
        │ → SYSTEM_ARCHITECTURE.md (10 min)      │
        └──────────────────────────────────────┘
              │
        ┌─────▼──────────────────────────────────┐
        │ Want detailed setup guide?             │
        │ → EMAIL_NOTIFICATION_GUIDE.md (20 min) │
        │ → QUICK_CHECKLIST.md (15 min)          │
        └──────────────────────────────────────┘
              │
        ┌─────▼──────────────────────────────────┐
        │ Having problems?                       │
        │ → IMPLEMENTATION_COMPLETE.md (15 min)  │
        │ → test_email_system.py (run script)    │
        └──────────────────────────────────────┘
```

---

## 📖 What Each Document Covers

### QUICK_REFERENCE.md

- How to start the system
- Frontend pages overview
- API endpoints summary
- Configuration values
- Troubleshooting table
- Common tasks
- **Best for:** Quick lookup, cheat sheet

### README_COMPLETE.md

- What is FloorEye
- Features overview
- Technology stack
- File structure
- How it works (step-by-step)
- Configuration details
- Performance expectations
- Getting started guide
- **Best for:** Understanding the big picture

### IMPLEMENTATION_COMPLETE.md

- What has been implemented
- System architecture diagram
- Quick start instructions
- Verification checklist
- Email notification details
- Troubleshooting guide
- Security notes
- **Best for:** Verifying system is ready, troubleshooting

### EMAIL_NOTIFICATION_GUIDE.md

- System architecture explanation
- Complete setup instructions
- Step-by-step verification
- Rate-limiting explanation
- Database queries for debugging
- Troubleshooting section
- Performance expectations
- **Best for:** Complete setup guide with all details

### SYSTEM_ARCHITECTURE.md

- Data flow diagrams
- Component interaction diagrams
- Request/response flow
- Database schema
- Configuration table
- File locations
- Quick start checklist
- **Best for:** Understanding system design

### QUICK_CHECKLIST.md

- Pre-launch verification
- Launch sequence (step-by-step)
- Data entry & testing (step-by-step)
- Troubleshooting checklist
- Success criteria
- Performance expectations
- **Best for:** Step-by-step verification

---

## 🎯 Choose Your Path

### Path 1: I Just Want to Start (5 minutes)

1. Double-click `START_FLOOREYE.bat`
2. Read `QUICK_REFERENCE.md`
3. Open http://127.0.0.1:5173

### Path 2: I Want to Understand Everything (30 minutes)

1. Read `QUICK_REFERENCE.md` (2 min)
2. Read `README_COMPLETE.md` (10 min)
3. Read `SYSTEM_ARCHITECTURE.md` (10 min)
4. Skim `IMPLEMENTATION_COMPLETE.md` (8 min)

### Path 3: I Need Step-by-Step Instructions (20 minutes)

1. Read `QUICK_CHECKLIST.md` from start
2. Follow each step
3. Verify with `test_email_system.py`

### Path 4: Something's Not Working (15 minutes)

1. Run `python test_email_system.py`
2. Check relevant section in `IMPLEMENTATION_COMPLETE.md` troubleshooting
3. Look at backend logs
4. Check `EMAIL_NOTIFICATION_GUIDE.md` troubleshooting section

---

## 💾 Code Files (Quick Reference)

### Frontend Pages

- **CamerasPage.tsx** - Manage cameras (add, toggle, delete)
- **NotificationsPage.tsx** - Manage email recipients (add, toggle, delete)
- **UploadPage.tsx** - Upload single image for detection
- **LiveCameraPage.tsx** - View live camera streams
- **HistoryPage.tsx** - View detection history

### Backend Endpoints

- **GET /cameras** - List cameras
- **POST /cameras** - Create camera
- **PATCH /cameras/{id}** - Update camera
- **DELETE /cameras/{id}** - Delete camera
- **GET /email-recipients** - List recipients
- **POST /email-recipients** - Create recipient
- **PATCH /email-recipients/{id}** - Toggle recipient
- **DELETE /email-recipients/{id}** - Delete recipient
- **GET /email-recipients/test** - Send test email
- **GET /health** - Health check

### Key Backend Services

- **monitor_service.py** - Detection loop + email sending
- **email_service.py** - SMTP email logic
- **detector.py** - YOLO detection

### Key Frontend Services

- **camera.service.ts** - Camera API calls
- **email.service.ts** - Email recipient API calls
- **detection.service.ts** - Detection API calls
- **history.service.ts** - History API calls

---

## 🔗 Quick Links

| What              | Where                         |
| ----------------- | ----------------------------- |
| Start system      | `START_FLOOREYE.bat`          |
| Test system       | `python test_email_system.py` |
| One-page guide    | `QUICK_REFERENCE.md`          |
| Complete overview | `README_COMPLETE.md`          |
| Setup guide       | `EMAIL_NOTIFICATION_GUIDE.md` |
| Step-by-step      | `QUICK_CHECKLIST.md`          |
| System design     | `SYSTEM_ARCHITECTURE.md`      |
| Check status      | `IMPLEMENTATION_COMPLETE.md`  |
| Frontend UI       | http://127.0.0.1:5173         |
| Backend API       | http://127.0.0.1:8000         |
| Health check      | http://127.0.0.1:8000/health  |

---

## 📋 Common Questions

**Q: How do I start the system?**
A: Double-click `START_FLOOREYE.bat` and open http://127.0.0.1:5173

**Q: Where is the setup guide?**
A: See `EMAIL_NOTIFICATION_GUIDE.md` for detailed setup

**Q: How do I test if email is working?**
A: Run `python test_email_system.py`

**Q: How do I verify the system?**
A: Follow `QUICK_CHECKLIST.md` step-by-step

**Q: What do I do if something breaks?**
A: Check troubleshooting section in `IMPLEMENTATION_COMPLETE.md`

**Q: Where is the API documentation?**
A: See endpoints section in `QUICK_REFERENCE.md` or detailed list in `EMAIL_NOTIFICATION_GUIDE.md`

**Q: How does detection work?**
A: See "How It Works" section in `README_COMPLETE.md` or diagrams in `SYSTEM_ARCHITECTURE.md`

**Q: Why is the monitor thread polling every 5 seconds?**
A: It's a balance between responsiveness and CPU usage. See `EMAIL_NOTIFICATION_GUIDE.md`

---

## ✅ System Status

- ✅ All documentation complete
- ✅ All code files in place
- ✅ All endpoints implemented
- ✅ All UI pages created
- ✅ All services working
- ✅ Ready to use!

---

## 🎓 Learn More

For specific topics:

- **Email notifications:** `EMAIL_NOTIFICATION_GUIDE.md`
- **System design:** `SYSTEM_ARCHITECTURE.md`
- **Step-by-step setup:** `QUICK_CHECKLIST.md`
- **Troubleshooting:** `IMPLEMENTATION_COMPLETE.md`
- **API reference:** `QUICK_REFERENCE.md`

---

## 📞 Need Help?

1. **Quick reference?** → `QUICK_REFERENCE.md`
2. **Setup guide?** → `EMAIL_NOTIFICATION_GUIDE.md`
3. **Understanding system?** → `README_COMPLETE.md`
4. **Verification steps?** → `QUICK_CHECKLIST.md`
5. **System design?** → `SYSTEM_ARCHITECTURE.md`
6. **Troubleshooting?** → `IMPLEMENTATION_COMPLETE.md`
7. **Test system?** → `python test_email_system.py`

---

**Happy monitoring! 🚀**
