#!/usr/bin/env python
"""
Quick Email System Test Script
Tests each component of the email notification system independently
"""

import os
import sys
import time
from pathlib import Path

# Add Backend dir to path
backend_dir = Path(__file__).parent / "Backend"
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("FloorEye Email Notification System - Quick Test")
print("=" * 70)

# 1. Check .env
print("\n[1/6] Checking .env configuration...")
try:
    from dotenv import load_dotenv
    env_file = backend_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .env found: {env_file}")
    else:
        print(f"❌ .env NOT found at {env_file}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to load .env: {e}")
    sys.exit(1)

# 2. Check SMTP credentials
print("\n[2/6] Checking SMTP credentials...")
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")

if smtp_user and smtp_pass:
    print(f"✅ SMTP User: {smtp_user}")
    print(f"✅ SMTP Host: {smtp_host}:{smtp_port}")
    print(f"✅ SMTP Pass: {'*' * len(smtp_pass)} (hidden)")
else:
    print(f"❌ SMTP credentials missing!")
    print(f"   SMTP_USER: {smtp_user}")
    print(f"   SMTP_PASS: {smtp_pass}")
    sys.exit(1)

# 3. Check database connection
print("\n[3/6] Checking database connection...")
try:
    from store.db import get_connection
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT 1")
    cursor.close()
    conn.close()
    print("✅ Database connected successfully")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# 4. Check cameras
print("\n[4/6] Checking cameras table...")
try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cameras WHERE aktif=1")
    cameras = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if cameras:
        print(f"✅ Found {len(cameras)} active camera(s):")
        for cam in cameras:
            print(f"   - ID {cam['id']}: {cam['nama']} → {cam['link']}")
    else:
        print(f"⚠️  No active cameras found. Add camera via frontend (Kelola Kamera)")
except Exception as e:
    print(f"❌ Failed to check cameras: {e}")

# 5. Check email recipients
print("\n[5/6] Checking email recipients...")
try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM email_recipients WHERE active=1")
    emails = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if emails:
        print(f"✅ Found {len(emails)} active email recipient(s):")
        for email in emails:
            print(f"   - {email['email']}")
    else:
        print(f"⚠️  No active email recipients. Add via frontend (Notifikasi Email)")
except Exception as e:
    print(f"❌ Failed to check email recipients: {e}")

# 6. Test email sending
print("\n[6/6] Testing email sending...")
try:
    from services.email_service import send_email
    
    test_recipient = os.getenv("SMTP_USER")  # Send to self for test
    test_subject = "[FloorEye Test] Email System Working ✅"
    test_body = f"""
Test Email dari FloorEye System
Waktu Test: {time.strftime('%Y-%m-%d %H:%M:%S')}

Ini adalah email uji coba untuk memastikan sistem email bekerja.
Jika Anda menerima email ini, maka sistem notifikasi siap digunakan.

---
FloorEye Monitoring System
"""
    
    print(f"Sending test email to {test_recipient}...")
    result = send_email(test_subject, test_body, [test_recipient])
    
    if result:
        print(f"✅ Email sent successfully!")
        print(f"   To: {test_recipient}")
        print(f"   Subject: {test_subject}")
        print(f"\n   Check your inbox (or spam folder) in ~30 seconds")
    else:
        print(f"❌ Email sending failed. Check backend logs above.")
except Exception as e:
    print(f"❌ Email test error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test Summary:")
print("=" * 70)
print("""
If all checks passed (✅):
  1. Start backend: python -m uvicorn app:app --reload
  2. Start frontend: npm run dev
  3. Monitor thread will detect dirty floor and send emails every 60 seconds
  
If any check failed (❌):
  1. Fix the configuration (check .env, DB tables, credentials)
  2. Re-run this test script
  3. Check backend logs for SMTP errors

Email flow should be:
  Camera → Monitor Thread → Dirty Detection → Email to Recipients
  
For more details, see: EMAIL_NOTIFICATION_GUIDE.md
""")
print("=" * 70)
