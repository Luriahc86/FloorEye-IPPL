# 📧 FloorEye Email Notification System - Complete Setup & Verification Guide

## System Architecture

```
Camera (RTSP)
    ↓
Monitor Thread (polls every 5 sec)
    ↓
detect_dirty_floor() [YOLO]
    ↓
Insert Event to DB (floor_events table)
    ↓
Send Email to Active Recipients
    ↓
Gmail Inbox ✅
```

## Configuration Checklist

### 1. Backend `.env` Configuration (Already Set)

```dotenv
# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=
DB_NAME=floor_eye

# Email (SMTP Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=flooreye.ippl505@gmail.com
SMTP_PASS=msbzmeucsrxeoipy

# Rate-limiting
NOTIFY_INTERVAL=60  # Seconds between notifications for same camera
```

### 2. Database Tables (Must Exist)

Run this in MySQL if tables missing:

```sql
-- Cameras table
CREATE TABLE IF NOT EXISTS cameras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(255) NOT NULL,
  lokasi VARCHAR(255),
  link VARCHAR(255) NOT NULL,
  aktif TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email recipients table
CREATE TABLE IF NOT EXISTS email_recipients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  active TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detection events table
CREATE TABLE IF NOT EXISTS floor_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(255),
  is_dirty TINYINT,
  confidence FLOAT,
  notes TEXT,
  image_path VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Step-by-Step Verification

### Step 1: Start Backend Server

```bash
cd D:\IPPL\FloorEye\Backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**

```
[INFO] Monitor thread started
[DEBUG] Found 0 cameras, 0 email recipients
[DEBUG] Found 0 cameras, 0 email recipients
...
```

### Step 2: Start Frontend (in another terminal)

```bash
cd D:\IPPL\FloorEye\Frontend
npm run dev
```

Navigate to: http://127.0.0.1:5173

### Step 3: Add Test Camera

1. Click **"🎥 Kelola Kamera"** (Manage Cameras)
2. Fill form:
   - **Nama**: "Test Ruang 1"
   - **Lokasi**: "Lantai 1"
   - **Link**: Use test video path or RTSP URL:
     - Option A: `D:\IPPL\FloorEye\Backend\assets\test_video.mp4` (if exists)
     - Option B: Real RTSP URL from camera
     - Option C: `0` (webcam if available)
   - **Aktif**: ✅ (checked)
3. Click **"Tambah Kamera"** button

**Backend log should show:**

```
[DEBUG] Found 1 cameras, 0 email recipients
```

### Step 4: Add Email Recipient

1. Click **"🔔 Notifikasi Email"** (Notifications)
2. Fill form:
   - **Email**: Your Gmail address (or test Gmail)
   - **Status**: ✅ Aktif (checked)
3. Click **"Tambah Email"** button

**Backend log should show:**

```
[DEBUG] Found 1 cameras, 1 email recipients
```

### Step 5: Wait for Detection

The monitor thread:

- Polls every **5 seconds**
- Captures frame from camera
- Runs YOLO detection for dirty floor
- If detected: sends email after checking rate-limit (NOTIFY_INTERVAL=60 sec)

**Backend log when dirty floor detected:**

```
[DEBUG] Processing camera 1: D:\IPPL\FloorEye\Backend\assets\test_video.mp4
[DEBUG] Camera 1 dirty=True
[INFO] Sending alert to 1 recipients (no attachment)
[INFO] Building email: to=['your-email@gmail.com'], subject=[FloorEye] Lantai Kotor Terdeteksi (Test Ruang 1)
[INFO] Connecting to SMTP smtp.gmail.com:587
[INFO] EHLO sent
[INFO] STARTTLS OK
[INFO] Login OK
[INFO] Message sent via STARTTLS
[INFO] Email send result: True
```

### Step 6: Verify Email Received

Check **Gmail Inbox** within 30 seconds:

- **From**: flooreye.ippl505@gmail.com
- **Subject**: `[FloorEye] Lantai Kotor Terdeteksi (Test Ruang 1)`
- **Body**:
  ```
  Otomatis mendeteksi lantai kotor pada kamera Test Ruang 1 pada 2025-12-07 10:30:45.
  ```

**If email goes to SPAM:**

- Gmail may mark it as spam (especially with test credentials)
- Check **Spam/Promotions folder**
- Mark as "Not Spam" to whitelist sender

---

## Troubleshooting

### Problem: Monitor thread says "Found 0 cameras"

- **Check**: Frontend shows camera in list?
  - If NO: Camera not saved to DB. Check network error in browser console.
  - If YES: But backend shows 0, restart backend server.

### Problem: Monitor thread says "Found 1 cameras, 0 email recipients"

- **Check**: Frontend shows email in Notifikasi page?
  - If NO: Email not saved. Check form validation.
  - If YES: Email `active` column might be 0. Toggle to ON in frontend.

### Problem: Email not sent (backend log shows STARTTLS failed)

```
[WARN] STARTTLS failed: ... Trying SMTP_SSL on port 465...
[INFO] Message sent via SMTP_SSL
```

- This is **normal**! System falls back to SMTP_SSL automatically. Email still sent.

### Problem: Email not received even though backend log says "Email send result: True"

1. **Check Gmail Spam/Promotions folder**
2. **Check .env SMTP_PASS**:
   - Gmail requires **App Password** (not regular password) if 2FA enabled
   - Use: https://myaccount.google.com/apppasswords
   - Generate new app password for "Mail" → use in SMTP_PASS
3. **Test email endpoint directly**:
   ```bash
   curl http://127.0.0.1:8000/email-recipients/test
   ```
   Response should be: `{"sent": true, "recipients": ["your-email@gmail.com"]}`

### Problem: Email sent but received same email multiple times (spam?)

- **This is rate-limiting working correctly!**
- Monitor sends max 1 email per camera per 60 seconds (NOTIFY_INTERVAL)
- If camera continuously detects dirty: email every 60 sec (not spam)

### Problem: YOLO model not loading

```
[ERROR] YOLO detection error: ...
```

- Check `computer_vision/models/best.pt` exists
- Model must be trained on "dirty" or "kotor" class
- If missing: place trained YOLO model in that path

### Problem: Cannot capture frame from camera

```
[WARN] No frame from camera 1
```

- Check RTSP link is correct and accessible
- If local file path: ensure it exists
- If IP camera: ping camera, check auth, ensure network

---

## Rate-Limiting (Anti-Spam)

**How it works:**

- Each camera tracks last notification time in `last_notif` dict
- Before sending: check if `now - last_notif[cam_id] < NOTIFY_INTERVAL (60 sec)`
- If yes: skip, don't send duplicate
- If no: send new email and update timestamp

**Example:**

```
Time 0:00 → Dirty detected → Email #1 sent, last_notif[1]=0:00
Time 0:15 → Dirty still detected → Skip (15 < 60)
Time 0:45 → Dirty still detected → Skip (45 < 60)
Time 1:05 → Dirty still detected → Email #2 sent, last_notif[1]=1:05
Time 1:20 → Clean floor detected → No email, reset timer
Time 1:25 → Dirty detected again → Email #3 sent (new cycle)
```

**To change rate-limit:**
Edit `.env`:

```dotenv
NOTIFY_INTERVAL=30  # Change to 30 seconds (more emails)
NOTIFY_INTERVAL=300 # Change to 5 minutes (fewer emails)
```

---

## Database Queries (For Debugging)

### Check cameras

```sql
SELECT * FROM cameras;
```

Must have at least one row with `aktif=1`.

### Check email recipients

```sql
SELECT * FROM email_recipients;
```

Must have at least one row with `active=1`.

### Check detection events

```sql
SELECT * FROM floor_events ORDER BY created_at DESC LIMIT 10;
```

Should see new rows with `is_dirty=1` when floor detected.

### Check email was sent but not received (check recipient toggle)

```sql
UPDATE email_recipients SET active=1 WHERE email='your@email.com';
```

---

## Manual Email Test

Send test email to all active recipients:

```bash
curl http://127.0.0.1:8000/email-recipients/test
```

**Success response:**

```json
{ "sent": true, "recipients": ["your-email@gmail.com"] }
```

**Failure response:**

```json
{ "sent": false, "recipients": [] }
```

---

## Summary

✅ **System Ready When:**

1. Backend running (monitor thread shows "Found N cameras, M email recipients")
2. At least 1 camera with `aktif=1` in DB
3. At least 1 email with `active=1` in DB
4. YOLO model file exists at `computer_vision/models/best.pt`
5. `.env` SMTP credentials set

✅ **Email Flows When:**

1. Monitor detects `dirty=True` from frame
2. Rate-limit allows (60+ seconds since last email for this camera)
3. At least 1 active recipient exists
4. SMTP connection successful (STARTTLS or SMTP_SSL)

✅ **Email Prevents Spam Via:**

- `NOTIFY_INTERVAL=60` per-camera throttle
- Only sends when dirty detected + rate-limit expired
- Not triggered by every frame (only on detection change)

---

## Contact & Logs

For detailed debugging:

1. Check backend terminal for all SMTP steps
2. Check `floor_events` table in DB for detection records
3. Test with `/email-recipients/test` endpoint directly
4. Verify email `active` toggle ON in NotificationsPage frontend

Good luck! 🚀
