# 🔍 DEBUGGING: Notifikasi Email Tidak Terkirim

Saya akan membantu Anda menemukan masalahnya. Mari lakukan diagnosis step-by-step.

---

## ⚡ Quick Diagnosis (5 menit)

### Step 1: Test Script Diagnostic

Jalankan script diagnostic:

```bash
cd D:\IPPL\FloorEye\Backend
python diagnose_email.py
```

**Output yang harus diperhatikan:**

```
[1/6] Checking SMTP configuration...
     ✅ atau ❌ - Lihat status ini

[2/6] Checking database connection...
     ✅ atau ❌ - Lihat status ini

[3/6] Checking email recipients...
     📧 Active recipients: X
     Jika = 0, masalah ditemukan!

[4/6] Checking active cameras...
     📹 Active cameras: X
     Jika = 0, masalah ditemukan!

[5/6] Checking detection history...
     📊 Total events: X
     Lihat ada deteksi atau tidak

[6/6] Testing email sending...
     ✅ atau ❌ - Ini test kirim email
```

---

## 🔧 Common Issues & Solutions

### Issue 1: ❌ No Active Email Recipients

**Gejala:**

```
[3/6] Checking email recipients...
     📧 Active recipients: 0
     ⚠️ WARNING: No active recipients!
```

**Solusi:**

1. Buka: http://127.0.0.1:5173
2. Klik: **"🔔 Notifikasi Email"**
3. Isi email: `your-email@gmail.com`
4. **Pastikan toggle AKTIF (centang biru)** ✅
5. Klik: **Tambah Email**
6. Run diagnostic lagi

---

### Issue 2: ❌ No Active Cameras

**Gejala:**

```
[4/6] Checking active cameras...
     📹 Active cameras: 0
     ⚠️ WARNING: No active cameras!
```

**Solusi:**

1. Buka: http://127.0.0.1:5173
2. Klik: **"🎥 Kelola Kamera"**
3. Isi form:
   - Nama: `Test Camera`
   - Lokasi: `Test`
   - Link: Gunakan salah satu:
     - `0` (webcam jika ada)
     - `D:\IPPL\FloorEye\Backend\assets\test_video.mp4` (jika ada file)
     - RTSP URL real camera
4. **Pastikan AKTIF (centang biru)** ✅
5. Klik: **Tambah Kamera**
6. Run diagnostic lagi

---

### Issue 3: ❌ SMTP Login Failed

**Gejala:**

```
[6/6] Testing email sending...
     ❌ SMTP_SSL also failed: [Errno -3] SSLError
     atau
     ❌ SMTP authentication failed
```

**Solusi:**

#### A. Check Gmail Credentials

```
1. Buka: https://myaccount.google.com/apppasswords
2. Jika 2FA belum aktif:
   - Setup 2FA dulu
   - Kembali ke apppasswords
3. Pilih: "Mail" + "Windows Computer"
4. Generate new password (16 chars)
5. Copy password
6. Edit Backend/.env:
   SMTP_PASS=<paste password baru>
7. Restart backend
```

#### B. Check Firewall

```bash
# Test koneksi ke Gmail SMTP
telnet smtp.gmail.com 587

# Jika gagal: firewall memblokir
# Solusi: Buka port 587 atau gunakan port 465
```

#### C. Check Port Configuration

```
Jika port 587 tidak bisa:
- Edit Backend/.env:
  SMTP_PORT=465

Note: Port 465 otomatis pakai SMTP_SSL
```

---

### Issue 4: ❌ No Detections

**Gejala:**

```
[5/6] Checking detection history...
     📊 Total events: 0
```

**Solusi:**

1. Check kamera bisa capture frame:

   - Jika pakai file: pastikan file ada
   - Jika pakai RTSP: test dengan VLC
   - Jika pakai webcam: test dengan Windows Camera

2. Monitor thread harus running (check backend terminal):

   ```
   [INFO] Monitor thread started
   [DEBUG] Found 1 cameras, 1 email recipients
   ```

3. Wait 5-30 detik untuk detection

4. Check database langsung:
   ```bash
   mysql -u root floor_eye -e "SELECT COUNT(*) FROM floor_events;"
   ```

---

## 📊 Checklist Debugging

```
✅ Requirement 1: Database Connection
   [ ] MySQL running (Laragon status)
   [ ] floor_eye database exists
   [ ] tables: cameras, email_recipients, floor_events exist

✅ Requirement 2: SMTP Configuration
   [ ] .env punya SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
   [ ] SMTP_PASS adalah App Password (bukan regular password)
   [ ] SMTP_HOST=smtp.gmail.com
   [ ] SMTP_PORT=587 (atau 465)

✅ Requirement 3: Email Recipients
   [ ] At least 1 email di email_recipients table
   [ ] Email punya active=1 (AKTIF)
   [ ] Email sudah verified di Gmail

✅ Requirement 4: Active Cameras
   [ ] At least 1 kamera di cameras table
   [ ] Kamera punya aktif=1 (AKTIF)
   [ ] Camera link accessible (RTSP atau file path valid)

✅ Requirement 5: Detection Working
   [ ] Monitor thread running (lihat backend logs)
   [ ] Dirty floor terdeteksi di camera
   [ ] Event inserted ke floor_events table

✅ Requirement 6: Email Sending
   [ ] send_email() function works (test endpoint returns ✅)
   [ ] Email diterima di Gmail (cek juga Spam folder)
```

---

## 🧪 Manual Test Steps

### Test 1: Database

```bash
mysql -u root floor_eye -e "SELECT email, active FROM email_recipients;"
```

Should show:

```
+-------------------+--------+
| email             | active |
+-------------------+--------+
| your-email@gmail.com |      1 |
+-------------------+--------+
```

### Test 2: SMTP Connection

```bash
cd D:\IPPL\FloorEye\Backend
python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    server.starttls()
    print('✅ SMTP Connection OK')
except Exception as e:
    print(f'❌ SMTP Connection Failed: {e}')
"
```

### Test 3: Email Sending

```bash
cd D:\IPPL\FloorEye\Backend
python -c "
from services.email_service import send_email
result = send_email(
    'Test',
    'Test email',
    ['your-email@gmail.com']
)
print(f'Result: {result}')
"
```

### Test 4: Monitor Detection

```
Watch backend terminal:
[DEBUG] Found X cameras, Y email recipients
[DEBUG] Camera 1 dirty=True  <- jika terdeteksi
[INFO] Sending alert...
[INFO] Email send result: True  <- jika berhasil kirim
```

---

## 🚨 If All Still Failing

1. **Check Backend Logs Carefully**

   - Lihat error message lengkap di terminal backend
   - Copy-paste error ke sini

2. **Check Gmail Settings**

   - Verify account: https://myaccount.google.com
   - Check 2FA status
   - Check Less secure app access (jika perlu)
   - Check recent activity

3. **Check Network**

   ```bash
   ping smtp.gmail.com
   # Jika not reaching: network issue
   ```

4. **Try Different Port**
   - Default: 587 (STARTTLS)
   - Fallback: 465 (SMTP_SSL)
   - Edit .env dan restart

---

## 📝 Detailed Manual Test (If Diagnostic Script Fails)

1. **Test .env loaded:**

   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SMTP_USER'))"
   ```

2. **Test database:**

   ```bash
   python -c "from store.db import get_connection; conn = get_connection(); print('OK')"
   ```

3. **Test email service:**

   ```bash
   python -c "
   from services.email_service import send_email
   result = send_email('Test', 'Test', ['your-email@gmail.com'])
   print(f'Sent: {result}')
   "
   ```

4. **Test monitor thread:**
   ```bash
   python -c "
   import os
   os.environ['NOTIFY_INTERVAL'] = '5'  # Quick test
   from services.monitor_service import monitor_loop
   import threading
   stop = threading.Event()
   # Let it run 10 seconds then stop
   monitor_loop(stop)
   "
   ```

---

## 🎯 Success Indicators

✅ **Diagnostic script shows:**

- [3/6] Active recipients: >= 1
- [4/6] Active cameras: >= 1
- [6/6] ✅ Email sent successfully!

✅ **Monitor logs show:**

```
[DEBUG] Found 1 cameras, 1 email recipients
[DEBUG] Camera 1 dirty=True
[INFO] Sending alert to 1 recipients
[INFO] Email send result: True
```

✅ **Email received:**

- Subject: `[FloorEye] Lantai Kotor Terdeteksi (...)`
- Body: Timestamp + camera name
- Time: Within 60 seconds of detection

---

**JALANKAN DIAGNOSTIC SCRIPT SEKARANG:**

```bash
python diagnose_email.py
```

**Kemudian share output untuk bantuan lebih lanjut!**
