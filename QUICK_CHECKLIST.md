# ✅ FloorEye Email Notification System - Quick Checklist

## Pre-Launch Verification (Run BEFORE starting system)

### 1. Environment Setup

- [ ] Backend folder: `D:\IPPL\FloorEye\Backend`
- [ ] Frontend folder: `D:\IPPL\FloorEye\Frontend`
- [ ] `.env` file exists in Backend folder with SMTP credentials
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed

### 2. Python Dependencies

```bash
cd D:\IPPL\FloorEye\Backend
pip install -r requirements.txt
```

Expected packages: fastapi, uvicorn, opencv-python, ultralytics, mysql-connector-python, python-dotenv

- [ ] All packages installed without errors

### 3. Database Check

```bash
# Open MySQL CLI
mysql -u root -p floor_eye

# Then run:
SHOW TABLES;
SELECT COUNT(*) FROM cameras;
SELECT COUNT(*) FROM email_recipients;
SELECT COUNT(*) FROM floor_events;
```

- [ ] `cameras` table exists and accessible
- [ ] `email_recipients` table exists and accessible
- [ ] `floor_events` table exists and accessible

### 4. YOLO Model

- [ ] File exists: `Backend/computer_vision/models/best.pt`
- [ ] File size > 100 MB (typical YOLO model)
- [ ] Model is trained to detect "dirty" or "kotor" class

### 5. SMTP Credentials (.env)

- [ ] `SMTP_HOST=smtp.gmail.com` ✅
- [ ] `SMTP_PORT=587` ✅
- [ ] `SMTP_USER=flooreye.ippl505@gmail.com` ✅
- [ ] `SMTP_PASS=msbzmeucsrxeoipy` ✅ (Gmail App Password, not regular password)
- [ ] `NOTIFY_INTERVAL=60` ✅

**Note:** If Gmail has 2FA enabled, use App Password:

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate new password
4. Use that password in SMTP_PASS

- [ ] SMTP credentials verified correct

---

## Launch Sequence

### Step 1: Start Backend

```bash
cd D:\IPPL\FloorEye\Backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Expected output:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
[INFO] Monitor thread started
[DEBUG] Found 0 cameras, 0 email recipients
[DEBUG] Found 0 cameras, 0 email recipients
INFO:     Application startup complete
```

- [ ] Backend running on http://127.0.0.1:8000
- [ ] Monitor thread says "started"
- [ ] Check `/health` endpoint: http://127.0.0.1:8000/health → `{"status": "healthy"}`

### Step 2: Start Frontend (in another terminal)

```bash
cd D:\IPPL\FloorEye\Frontend
npm run dev
```

Expected output:

```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  press h to show help
```

- [ ] Frontend running on http://127.0.0.1:5173
- [ ] Open http://127.0.0.1:5173 in browser
- [ ] No console errors visible

### Step 3: Test Backend Health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{ "status": "healthy" }
```

- [ ] Backend responds with status: healthy

---

## Data Entry & Testing

### Step 4: Add Test Camera

1. Open http://127.0.0.1:5173
2. Click **"🎥 Kelola Kamera"** (Manage Cameras)
3. Fill form:
   - **Nama**: "Test Camera 1"
   - **Lokasi**: "Ruang Test"
   - **Link**: Choose one:
     - `0` (webcam if available on your PC)
     - `D:\IPPL\FloorEye\Backend\assets\test_video.mp4` (if file exists)
     - `rtsp://192.168.1.100:554/stream` (real camera)
   - **Aktif**: ✅ (checked)
4. Click **"Tambah Kamera"** button

Expected:

- Camera appears in list below
- No error message

- [ ] Camera added successfully
- [ ] Camera shows "✅ Aktif" status

### Step 5: Check Backend Logs

Look at backend terminal, should now show:

```
[DEBUG] Found 1 cameras, 0 email recipients
```

- [ ] Backend now shows "Found 1 cameras"

### Step 6: Add Test Email Recipient

1. Click **"🔔 Notifikasi Email"** (Notifications)
2. Fill form:
   - **Email**: Your Gmail address (must be Gmail)
   - **Status**: ✅ Aktif (checked)
3. Click **"Tambah Email"** button

Expected:

- Email appears in list below
- Shows "✅ Aktif" status
- No error message

- [ ] Email recipient added successfully
- [ ] Status shows "✅ Aktif"

### Step 7: Check Backend Logs Again

Backend terminal should show:

```
[DEBUG] Found 1 cameras, 1 email recipients
```

- [ ] Backend now shows "Found 1 cameras, 1 email recipients"

### Step 8: Send Test Email

```bash
curl http://127.0.0.1:8000/email-recipients/test
```

Expected response:

```json
{ "sent": true, "recipients": ["your-email@gmail.com"] }
```

Backend terminal should show:

```
[INFO] Building email: to=['your-email@gmail.com'], subject=[FloorEye] Test Email
[INFO] Connecting to SMTP smtp.gmail.com:587
[INFO] EHLO sent
[INFO] STARTTLS OK
[INFO] Login OK
[INFO] Message sent via STARTTLS
[INFO] Email send result: True
```

- [ ] `"sent": true` in response
- [ ] Backend shows email sent successfully
- [ ] Check your Gmail inbox within 30 seconds for test email

### Step 9: Verify Test Email Received

1. Open your Gmail inbox
2. Look for email from: `flooreye.ippl505@gmail.com`
3. Subject: `[FloorEye] Test Email`

Expected email body:

```
Ini adalah email test dari FloorEye. Jika kamu menerima ini, email notifikasi berhasil dikonfigurasi!
```

- [ ] Test email received in inbox
- [ ] Check it's not in Spam folder
- [ ] If in Spam, mark "Not Spam" to whitelist sender

### Step 10: Wait for Automatic Detection

Monitor thread polls active cameras every 5 seconds for dirty floor.

Backend terminal should show (every 5 seconds):

```
[DEBUG] Found 1 cameras, 1 email recipients
[DEBUG] Processing camera 1: 0
[DEBUG] Camera 1 dirty=False  (or dirty=True if floor detected)
```

When dirty floor is detected:

```
[DEBUG] Camera 1 dirty=True
[INFO] Sending alert to 1 recipients (no attachment)
[INFO] Building email: to=['your-email@gmail.com'], subject=[FloorEye] Lantai Kotor Terdeteksi (Test Camera 1)
[INFO] Connecting to SMTP smtp.gmail.com:587
[INFO] EHLO sent
[INFO] STARTTLS OK
[INFO] Login OK
[INFO] Message sent via STARTTLS
[INFO] Email send result: True
```

Expected notification email:

- **From**: flooreye.ippl505@gmail.com
- **Subject**: `[FloorEye] Lantai Kotor Terdeteksi (Test Camera 1)`
- **Body**:

  ```
  Otomatis mendeteksi lantai kotor pada kamera Test Camera 1 pada 2025-12-07 10:30:45.
  ```

- [ ] Wait 5-30 seconds for notification email
- [ ] Check inbox for dirty floor notification
- [ ] Email received with correct subject and camera name

### Step 11: Verify Rate-Limiting (Anti-Spam)

If camera still shows dirty floor, monitor will wait 60 seconds before sending next email.

- [ ] First email sent at time T
- [ ] Wait 30 seconds → no second email (rate-limiting works)
- [ ] Wait to time T+60 → second email sent (if floor still dirty)
- [ ] Check backend logs show "last_notif" tracking

- [ ] Rate-limiting prevents email spam ✅

---

## Troubleshooting Checklist

### Issue: Backend won't start

- [ ] Python 3.8+ installed: `python --version`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Port 8000 not in use: `netstat -ano | findstr :8000`
- [ ] `.env` file in Backend folder
- [ ] No syntax errors: Try `python -c "from app import app"`

### Issue: Frontend won't start

- [ ] Node.js 18+ installed: `node --version`
- [ ] Dependencies installed: `npm install`
- [ ] Port 5173 not in use: `netstat -ano | findstr :5173`
- [ ] No TypeScript errors: `npm run build`

### Issue: Database connection fails

- [ ] MySQL running: Check Laragon status
- [ ] Database exists: `mysql -u root -e "SHOW DATABASES;"`
- [ ] Credentials in .env correct: `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- [ ] Tables created: `mysql -u root floor_eye -e "SHOW TABLES;"`

### Issue: Email test endpoint returns `"sent": false`

- [ ] SMTP credentials in .env correct
- [ ] Gmail account has 2FA → use App Password in SMTP_PASS
- [ ] Port 587 open (firewall check)
- [ ] Check backend logs for SMTP error details
- [ ] Try SMTP_SSL fallback: Check logs for "SMTP_SSL OK"

### Issue: Test email goes to Spam

- [ ] Normal for first test (Gmail filters unknown senders)
- [ ] Mark as "Not Spam" in Gmail
- [ ] Future emails should go to Inbox
- [ ] Wait 24 hours for Gmail to trust sender

### Issue: Camera not detected in monitor

- [ ] Camera `aktif=1` in database: Check DB directly
- [ ] RTSP link accessible: Test with `ffmpeg` or `vlc`
- [ ] File path exists (if using local file): Check file exists
- [ ] Monitor thread running: Backend logs should show "Found N cameras"

### Issue: No "dirty floor detected" notification

- [ ] YOLO model file exists: `Backend/computer_vision/models/best.pt`
- [ ] Model trained on "dirty"/"kotor" class
- [ ] Camera showing actual dirty floor (if using webcam)
- [ ] YOLO confidence threshold 0.25 (check detector.py)
- [ ] Check backend logs for detection score: `[DEBUG] Camera 1 dirty=False/True`

---

## Success Criteria ✅

**System is working when:**

1. ✅ Backend runs without errors
2. ✅ Frontend loads in browser
3. ✅ Can add camera via UI
4. ✅ Can add email recipient via UI
5. ✅ Backend logs show "Found N cameras, M email recipients"
6. ✅ Test email endpoint sends email successfully
7. ✅ Test email received in Gmail inbox (or spam folder)
8. ✅ Monitor detects dirty floor and logs "dirty=True"
9. ✅ Notification email received for dirty floor detection
10. ✅ No duplicate emails within 60 seconds (rate-limiting works)

---

## Performance Expectations

| Operation         | Time      | Notes                               |
| ----------------- | --------- | ----------------------------------- |
| Backend startup   | 3-5 sec   | Monitor thread starts after 1-2 sec |
| Frontend load     | 2-4 sec   | First time takes longer (webpack)   |
| Add camera        | < 1 sec   | Instant, no refresh needed          |
| Add email         | < 1 sec   | Instant, no refresh needed          |
| Monitor cycle     | 5 sec     | Polls every 5 seconds               |
| Detection latency | 2-5 sec   | YOLO inference on GPU/CPU           |
| Email latency     | 5-30 sec  | Depends on Gmail SMTP               |
| Email received    | 30-60 sec | Total from detection to inbox       |
| Rate-limiting     | 60 sec    | Minimum gap between emails          |

---

## Contact & Support

If something doesn't work:

1. Check backend logs (terminal)
2. Run: `curl http://127.0.0.1:8000/health` → should return healthy
3. Run: `curl http://127.0.0.1:8000/email-recipients/test` → test email
4. Check database: `mysql -u root floor_eye -e "SELECT * FROM email_recipients;"`
5. Verify YOLO model: `ls -la Backend/computer_vision/models/best.pt`

For detailed documentation, see:

- `EMAIL_NOTIFICATION_GUIDE.md` — Complete setup guide
- `SYSTEM_ARCHITECTURE.md` — System diagrams and data flow
- `Backend/services/email_service.py` — SMTP logic with logging
- `Backend/services/monitor_service.py` — Detection + notification logic

Good luck! 🚀
