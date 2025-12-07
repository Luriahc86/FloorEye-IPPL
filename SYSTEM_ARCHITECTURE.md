# 📊 FloorEye System Architecture Diagram

## Data Flow: Camera → Detection → Email

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MONITORING PIPELINE                             │
└─────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   CAMERA     │
     │   (RTSP)     │
     └──────┬───────┘
            │
            │ Capture Frame (every 5 sec)
            │
            ▼
     ┌──────────────────────┐
     │  Monitor Thread      │
     │  monitor_loop()      │
     └──────┬───────────────┘
            │
            │ Loop:
            │ 1. Get active cameras from DB
            │ 2. Get active email recipients from DB
            │ 3. For each camera:
            │    - Capture frame from RTSP
            │    - Check rate-limit (60 sec)
            │    - Run YOLO detection
            │
            ▼
     ┌──────────────────────┐
     │  YOLO Detector       │
     │  detect_dirty_floor()│
     └──────┬───────────────┘
            │
            │ Return: True/False
            │
            ▼
    ╔════════════════════════╗
    ║ DIRTY FLOOR DETECTED?  ║
    ╚═════┬──────────────┬═══╝
          │ YES          │ NO
          │              │
          ▼              ▼
    ┌─────────────┐    SKIP
    │ Insert to DB│
    │ floor_events│
    └──────┬──────┘
           │
           ▼
    ┌──────────────────────┐
    │  Send Email          │
    │  send_email()        │
    │  to active           │
    │  recipients          │
    └──────┬───────────────┘
           │
           ├─ SMTP (TLS port 587)
           │  ├─ EHLO
           │  ├─ STARTTLS
           │  ├─ LOGIN (flooreye.ippl505@gmail.com)
           │  ├─ SEND MESSAGE
           │  └─ QUIT
           │
           │  [If STARTTLS fails, fallback to:]
           │
           └─ SMTP_SSL (SSL port 465)
              ├─ EHLO
              ├─ LOGIN
              ├─ SEND MESSAGE
              └─ QUIT
                 │
                 ▼
         ┌──────────────────┐
         │  Gmail Inbox ✅  │
         │  Recipients      │
         └──────────────────┘

```

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Frontend (React)                     Backend (FastAPI)          │
│  ─────────────────                    ──────────────────          │
│                                                                   │
│  ┌──────────────────┐                ┌─────────────────────┐    │
│  │  Sidebar         │────────────────│  app.py             │    │
│  │  - Kelola Kamera │                │  - Route handlers   │    │
│  │  - Notifikasi    │                │  - Lifespan (start  │    │
│  └──────────────────┘                │    monitor thread)  │    │
│         │                            └────────┬────────────┘    │
│         │                                     │                  │
│         ▼                                     ▼                  │
│  ┌──────────────────┐                ┌─────────────────────┐    │
│  │ CamerasPage.tsx  │                │ camera_routes.py    │    │
│  │ - Add camera     │──────POST──────│ - GET /cameras      │    │
│  │ - Toggle aktif   │──────PATCH─────│ - POST /cameras     │    │
│  │ - Delete camera  │──────DELETE────│ - DELETE /cameras/{id}   │
│  └──────────────────┘                │ - PATCH /cameras/{id}    │
│         │                            └─────────┬──────────┘    │
│         │                                      │                 │
│         ▼                                      ▼                 │
│  ┌──────────────────┐                ┌─────────────────────┐    │
│  │NotificationsPage │                │ email_routes.py     │    │
│  │ - Add email      │──────POST──────│ - GET /email-       │    │
│  │ - Toggle active  │──────PATCH─────│   recipients        │    │
│  │ - Delete email   │──────DELETE────│ - POST /email-      │    │
│  └──────────────────┘                │   recipients        │    │
│                                       │ - PATCH /email-     │    │
│                                       │   recipients/{id}   │    │
│                                       │ - DELETE /email-    │    │
│                                       │   recipients/{id}   │    │
│                                       │ - GET /email-       │    │
│                                       │   recipients/test   │    │
│                                       └─────────┬──────────┘    │
│                                                 │                 │
│                                                 ▼                 │
│                                       ┌─────────────────────┐    │
│                                       │MySQL Database       │    │
│                                       │ - cameras table     │    │
│                                       │ - email_recipients  │    │
│                                       │ - floor_events      │    │
│                                       └─────────────────────┘    │
│                                                 │                 │
│                                                 │ 5 sec polling   │
│                                                 │ for active data │
│                                                 │                 │
│                                                 ▼                 │
│                                       ┌─────────────────────┐    │
│                                       │ monitor_service.py  │    │
│                                       │ - Get cameras       │    │
│                                       │ - Get email recips  │    │
│                                       │ - Check rate-limit  │    │
│                                       │ - Capture frame     │    │
│                                       │ - Run detection     │    │
│                                       │ - Send email        │    │
│                                       └─────────┬──────────┘    │
│                                                 │                 │
│                                                 ▼                 │
│                                       ┌─────────────────────┐    │
│                                       │ detector.py (YOLO)  │    │
│                                       │ - detect_dirty_     │    │
│                                       │   floor()           │    │
│                                       └────────┬────────────┘    │
│                                                │                  │
│                                                ▼                  │
│                                       ┌─────────────────────┐    │
│                                       │email_service.py     │    │
│                                       │ - Build EmailMsg    │    │
│                                       │ - STARTTLS (587)    │    │
│                                       │ - Fallback SSL(465) │    │
│                                       │ - Send via Gmail    │    │
│                                       └─────────┬──────────┘    │
│                                                 │                 │
│                                                 ▼                 │
│                                       ┌─────────────────────┐    │
│                                       │  Gmail SMTP Server  │    │
│                                       │ smtp.gmail.com      │    │
│                                       └────────┬────────────┘    │
│                                                 │                 │
│                                                 ▼                 │
│                                       📧 User Gmail Inbox ✅     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

```

---

## Request/Response Flow

### Adding a Camera (Frontend → Backend → DB)

```
Frontend (CamerasPage)
    │
    ├─ POST /cameras
    │  {
    │    "nama": "Ruang Tamu",
    │    "lokasi": "Lantai 1",
    │    "link": "rtsp://192.168.1.100:554/stream",
    │    "aktif": 1
    │  }
    │
    ▼
Backend (camera_routes.py)
    │
    ├─ Validate data
    ├─ Insert into cameras table
    │
    ▼
Database (floor_eye.cameras)
    │
    ├─ id: 1
    ├─ nama: "Ruang Tamu"
    ├─ lokasi: "Lantai 1"
    ├─ link: "rtsp://192.168.1.100:554/stream"
    ├─ aktif: 1 ✅
    │
    ▼
Monitor Thread (next cycle: 5 sec)
    │
    ├─ SELECT * FROM cameras WHERE aktif=1
    ├─ Found 1 camera
    ├─ Capture frame from rtsp://192.168.1.100:554/stream
    ├─ Run YOLO detection
    │
    └─ If dirty detected:
       ├─ Check rate-limit (60 sec)
       ├─ INSERT into floor_events
       ├─ Call send_email()
       └─ Update last_notif[1] = now
```

### Adding an Email Recipient (Frontend → Backend → DB)

```
Frontend (NotificationsPage)
    │
    ├─ POST /email-recipients
    │  {
    │    "email": "user@gmail.com",
    │    "active": 1
    │  }
    │
    ▼
Backend (email_routes.py)
    │
    ├─ Validate email
    ├─ Insert into email_recipients table
    │
    ▼
Database (floor_eye.email_recipients)
    │
    ├─ id: 1
    ├─ email: "user@gmail.com"
    ├─ active: 1 ✅
    │
    ▼
Monitor Thread (next cycle: 5 sec)
    │
    ├─ SELECT * FROM email_recipients WHERE active=1
    ├─ Found 1 recipient: "user@gmail.com"
    │
    └─ Ready to send notifications
```

### Dirty Floor Detection & Email (Monitor → YOLO → SMTP)

```
Monitor Thread (every 5 sec)
    │
    ├─ cv2.VideoCapture(camera_link)
    ├─ cap.read() → frame
    │
    ▼
YOLO Detection (detector.py)
    │
    ├─ model(frame)
    ├─ For each detection:
    │  ├─ Check label: "dirty" or "kotor"?
    │  ├─ Check confidence >= 0.25
    │
    ▼ YES (dirty detected)
    │
    ├─ Check rate-limit: now - last_notif[cam_id] >= 60?
    │
    ▼ YES (60+ seconds since last email)
    │
    ├─ INSERT floor_events (is_dirty=1)
    ├─ Call send_email()
    │  │
    │  ├─ GET active recipients from DB
    │  ├─ For each recipient:
    │  │  └─ Build EmailMessage
    │  │
    │  ├─ Try STARTTLS (port 587):
    │  │  ├─ SMTP("smtp.gmail.com", 587)
    │  │  ├─ ehlo()
    │  │  ├─ starttls()
    │  │  ├─ login(SMTP_USER, SMTP_PASS)
    │  │  ├─ send_message(msg)
    │  │
    │  └─ [If fails] Try SMTP_SSL (port 465):
    │     ├─ SMTP_SSL("smtp.gmail.com", 465)
    │     ├─ ehlo()
    │     ├─ login(SMTP_USER, SMTP_PASS)
    │     ├─ send_message(msg)
    │
    ▼
Gmail SMTP Server
    │
    ├─ Receive message
    ├─ Route to recipient inbox
    │
    ▼
📧 User Gmail Inbox ✅
```

---

## Database Schema

### cameras table

```sql
CREATE TABLE cameras (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nama VARCHAR(255),           -- Camera name
  lokasi VARCHAR(255),         -- Location
  link VARCHAR(255),           -- RTSP or file path
  aktif TINYINT DEFAULT 1,     -- 1=monitored, 0=inactive
  created_at TIMESTAMP
);
```

### email_recipients table

```sql
CREATE TABLE email_recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE,   -- Gmail address
  active TINYINT DEFAULT 1,    -- 1=receives notifications, 0=inactive
  created_at TIMESTAMP
);
```

### floor_events table

```sql
CREATE TABLE floor_events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  source VARCHAR(255),         -- "camera_1", "camera_2", etc.
  is_dirty TINYINT,            -- 1=dirty, 0=clean
  confidence FLOAT,            -- YOLO confidence score
  notes TEXT,                  -- Additional info
  image_path VARCHAR(255),     -- Empty string (DB-only, no files)
  created_at TIMESTAMP
);
```

---

## Key Configuration Values

| Setting           | Value        | Purpose                                       |
| ----------------- | ------------ | --------------------------------------------- |
| `NOTIFY_INTERVAL` | 60 (seconds) | Rate-limit: max 1 email per camera per minute |
| `SMTP_PORT`       | 587          | Gmail STARTTLS (port for TLS encryption)      |
| `SMTP_SSL_PORT`   | 465          | Gmail SMTP_SSL (fallback if 587 fails)        |
| `Monitor Poll`    | 5 (seconds)  | Check for dirty floor every 5 seconds         |
| `Email Timeout`   | 20 (seconds) | Wait max 20 sec for SMTP response             |
| `YOLO Threshold`  | 0.25         | Min confidence to report detection            |

---

## File Locations

```
D:\IPPL\FloorEye\
├── Backend/
│   ├── app.py                        ← Main FastAPI app
│   ├── .env                          ← Config: SMTP, DB, NOTIFY_INTERVAL
│   ├── requirements.txt              ← Python dependencies
│   ├── services/
│   │   ├── monitor_service.py        ← Background monitoring thread
│   │   └── email_service.py          ← SMTP email sending
│   ├── routes/
│   │   ├── camera_routes.py          ← Camera CRUD endpoints
│   │   ├── email_routes.py           ← Email recipient CRUD + test
│   │   ├── detection_routes.py       ← Detection endpoints
│   │   └── history_routes.py         ← History/event retrieval
│   ├── computer_vision/
│   │   ├── detector.py               ← YOLO dirty floor detection
│   │   └── models/
│   │       └── best.pt               ← Trained YOLO model
│   └── store/
│       ├── db.py                     ← Database connection pool
│       └── tabel.sql                 ← SQL schema
│
├── Frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CamerasPage.tsx       ← Camera management UI
│   │   │   └── NotificationsPage.tsx ← Email recipient management UI
│   │   ├── services/
│   │   │   ├── camera.service.ts     ← Camera API wrapper
│   │   │   └── email.service.ts      ← Email API wrapper
│   │   ├── components/
│   │   │   └── Sidebar.tsx           ← Navigation menu
│   │   └── router/
│   │       └── index.tsx             ← Route definitions
│   └── vite.config.js                ← Frontend build config
│
├── EMAIL_NOTIFICATION_GUIDE.md       ← This guide
├── test_email_system.py              ← Quick test script
└── desktop.ini
```

---

## Quick Start Checklist

- [ ] Backend running: `python -m uvicorn app:app --reload`
- [ ] Frontend running: `npm run dev`
- [ ] At least 1 camera with `aktif=1` in database
- [ ] At least 1 email with `active=1` in database
- [ ] YOLO model at `computer_vision/models/best.pt`
- [ ] `.env` has valid SMTP credentials
- [ ] Wait 5 seconds for monitor thread to detect
- [ ] Check Gmail inbox within 30 seconds
- [ ] Verify no duplicate emails (rate-limiting working)

✅ **System Ready!**
