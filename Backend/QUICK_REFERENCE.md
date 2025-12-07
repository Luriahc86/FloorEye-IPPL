# 🚀 FloorEye Quick Reference Card

## ⚡ Start System (Fastest Way)

```batch
cd D:\IPPL\FloorEye
START_FLOOREYE.bat
```

Then open: **http://127.0.0.1:5173**

---

## 📱 Frontend Pages

| Page              | URL            | What to Do                             |
| ----------------- | -------------- | -------------------------------------- |
| **Cameras**       | /cameras       | Add/edit/delete cameras for monitoring |
| **Notifications** | /notifications | Add/edit/delete email recipients       |
| **Upload**        | /upload        | Upload image for one-time detection    |
| **Live**          | /live          | View live camera streams               |
| **History**       | /history       | View past detection events             |

---

## 🔗 API Endpoints

### Cameras

```
GET    /cameras              ← List cameras
POST   /cameras              ← Create camera
PATCH  /cameras/{id}         ← Update camera
DELETE /cameras/{id}         ← Delete camera
```

### Email Recipients

```
GET    /email-recipients     ← List recipients
POST   /email-recipients     ← Add recipient
PATCH  /email-recipients/{id}← Toggle active
DELETE /email-recipients/{id}← Delete recipient
GET    /email-recipients/test← Send test email
```

### Health Check

```
GET    /health               ← System status
GET    /                     ← API info
```

---

## 📊 How Detection Works

```
1. Monitor thread runs every 5 seconds
2. Gets all cameras where aktif=1
3. For each camera:
   a) Capture frame from RTSP/file
   b) Run YOLO detection
   c) Check if "dirty" class detected
   d) If YES + rate-limit OK:
      - Insert event to floor_events table
      - Send email to all active recipients
      - Update rate-limit timestamp
   e) If NO or rate-limit blocked:
      - Skip (no email)
4. Sleep 5 seconds, repeat
```

---

## 💌 Email Notification

**When:** Automatic when dirty floor detected  
**To:** All email_recipients with active=1  
**Subject:** `[FloorEye] Lantai Kotor Terdeteksi (Camera Name)`  
**Body:** Detection timestamp + camera name  
**Rate-limit:** Max 1 email per camera per 60 seconds

---

## 🔧 Configuration (.env)

```dotenv
# Database
DB_HOST=127.0.0.1
DB_USER=root
DB_PASS=
DB_NAME=floor_eye

# Email (Gmail)
SMTP_USER=flooreye.ippl505@gmail.com
SMTP_PASS=msbzmeucsrxeoipy
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Rate-limiting
NOTIFY_INTERVAL=60  # seconds between emails
```

---

## ✅ Verification Checklist

Quick 1-minute check:

```bash
# 1. Test backend health
curl http://127.0.0.1:8000/health
# Expected: {"status": "healthy"}

# 2. Test email endpoint
curl http://127.0.0.1:8000/email-recipients/test
# Expected: {"sent": true, "recipients": [...]}

# 3. List cameras (via frontend)
# Should show camera added via CamerasPage

# 4. List emails (via frontend)
# Should show email added via NotificationsPage

# 5. Check Gmail inbox
# Should receive test email from endpoint above
```

---

## 🐛 Quick Troubleshooting

| Problem                 | Solution                                                |
| ----------------------- | ------------------------------------------------------- |
| Backend won't start     | Check port 8000 free: `netstat -ano \| find :8000`      |
| Frontend won't start    | Check port 5173 free, run `npm install`                 |
| Email not sending       | Check .env SMTP credentials, use Gmail App Password     |
| Test email goes to Spam | Mark "Not Spam", future emails go to Inbox              |
| No detection happening  | Check camera aktif=1, YOLO model exists                 |
| Duplicate emails sent   | Normal if you add same email twice, rate-limiting works |
| Database error          | Check MySQL running (Laragon), credentials in .env      |

---

## 🎯 Success Indicators

System is working when you see:

**Backend Terminal:**

```
[INFO] Monitor thread started
[DEBUG] Found 1 cameras, 1 email recipients
[DEBUG] Camera 1 dirty=True
[INFO] Email send result: True
```

**Gmail Inbox:**

```
From: flooreye.ippl505@gmail.com
Subject: [FloorEye] Lantai Kotor Terdeteksi (Camera Name)
Body: Otomatis mendeteksi lantai kotor pada kamera ...
```

---

## 📈 Performance

| Operation             | Time      |
| --------------------- | --------- |
| Monitor cycle         | 5 sec     |
| YOLO inference        | 2-5 sec   |
| Email send            | 5-30 sec  |
| Total: detect → inbox | 30-60 sec |

---

## 📞 Key Files

| File                                       | Purpose          |
| ------------------------------------------ | ---------------- |
| `Backend/app.py`                           | Main FastAPI app |
| `Backend/services/monitor_service.py`      | Detection loop   |
| `Backend/services/email_service.py`        | SMTP sending     |
| `Backend/.env`                             | Configuration    |
| `Frontend/src/pages/CamerasPage.tsx`       | Camera UI        |
| `Frontend/src/pages/NotificationsPage.tsx` | Email UI         |
| `test_email_system.py`                     | System test      |

---

## 🔗 Useful Links

| Link                                      | Purpose            |
| ----------------------------------------- | ------------------ |
| http://127.0.0.1:5173                     | Frontend UI        |
| http://127.0.0.1:8000                     | Backend API        |
| http://127.0.0.1:8000/health              | Health check       |
| https://myaccount.google.com/apppasswords | Gmail App Password |

---

## 📋 Common Tasks

### Add Camera

1. Frontend → Click "🎥 Kelola Kamera"
2. Fill: nama, lokasi, link (RTSP or file path)
3. Click "Tambah Kamera"
4. ✅ Camera monitored automatically

### Add Email

1. Frontend → Click "🔔 Notifikasi Email"
2. Fill: email (Gmail address)
3. Click "Tambah Email"
4. ✅ Will receive notifications

### Test Email

```bash
curl http://127.0.0.1:8000/email-recipients/test
```

### Check Logs

Look at backend terminal for detailed SMTP/detection logs

### Change Rate-Limit

Edit `.env` file:

```dotenv
NOTIFY_INTERVAL=30  # 30 seconds instead of 60
```

---

## 🌟 Status

- ✅ Backend: Implemented
- ✅ Frontend: Implemented
- ✅ Database: Implemented
- ✅ Detection: Implemented
- ✅ Email: Implemented
- ✅ Rate-limiting: Implemented
- ✅ Documentation: Complete

**System Status: READY TO USE** 🚀

---

## 🎓 Learn More

For detailed information, see:

- `README_COMPLETE.md` — Full system overview
- `EMAIL_NOTIFICATION_GUIDE.md` — Complete setup guide
- `QUICK_CHECKLIST.md` — Step-by-step verification
- `SYSTEM_ARCHITECTURE.md` — System diagrams

---

**Happy monitoring!** 📹✨
