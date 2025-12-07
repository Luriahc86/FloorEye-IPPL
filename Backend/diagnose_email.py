#!/usr/bin/env python
"""
Diagnostic script untuk FloorEye Email Notification System
Memeriksa setiap komponen untuk menemukan mengapa notifikasi tidak terkirim
"""

import os
import sys
import mysql.connector
from pathlib import Path

# Add Backend dir to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("FloorEye Email Notification System - Diagnostic")
print("=" * 70)

# 1. Load .env
print("\n[1/6] Loading .env configuration...")
try:
    from dotenv import load_dotenv
    env_file = backend_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ .env loaded from: {env_file}")
    else:
        print(f"❌ .env NOT found at {env_file}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error loading .env: {e}")
    sys.exit(1)

# 2. Check SMTP credentials
print("\n[2/6] Checking SMTP configuration...")
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")
smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
smtp_port = os.getenv("SMTP_PORT", "587")

if smtp_user and smtp_pass:
    print(f"✅ SMTP User: {smtp_user}")
    print(f"✅ SMTP Host: {smtp_host}:{smtp_port}")
    print(f"✅ SMTP Pass length: {len(smtp_pass)} characters")
else:
    print(f"❌ SMTP credentials missing!")
    print(f"   SMTP_USER: {smtp_user}")
    print(f"   SMTP_PASS: {smtp_pass}")
    sys.exit(1)

# 3. Check database connection
print("\n[3/6] Testing database connection...")
try:
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASS", "")
    db_name = os.getenv("DB_NAME", "floor_eye")
    
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    cursor = conn.cursor(dictionary=True)
    print(f"✅ Database connected: {db_host}:{db_port}/{db_name}")
    
    # Check cameras table
    cursor.execute("SELECT COUNT(*) as cnt FROM cameras")
    cam_count = cursor.fetchone()["cnt"]
    print(f"   Cameras table: {cam_count} records")
    
    cursor.execute("SELECT COUNT(*) as cnt FROM cameras WHERE aktif=1")
    active_cam_count = cursor.fetchone()["cnt"]
    print(f"   ✅ Active cameras: {active_cam_count}")
    
    if active_cam_count == 0:
        print(f"   ⚠️  WARNING: No active cameras! Add camera via frontend (Kelola Kamera)")
    
    # Check email recipients
    cursor.execute("SELECT COUNT(*) as cnt FROM email_recipients")
    email_count = cursor.fetchone()["cnt"]
    print(f"   Email recipients table: {email_count} records")
    
    cursor.execute("SELECT COUNT(*) as cnt FROM email_recipients WHERE active=1")
    active_email_count = cursor.fetchone()["cnt"]
    print(f"   ✅ Active recipients: {active_email_count}")
    
    if active_email_count == 0:
        print(f"   ⚠️  WARNING: No active email recipients! Add via frontend (Notifikasi Email)")
        # Check if any recipients exist but are inactive
        cursor.execute("SELECT email, active FROM email_recipients")
        all_emails = cursor.fetchall()
        if all_emails:
            print(f"   Found {len(all_emails)} inactive recipient(s):")
            for email_rec in all_emails:
                print(f"      - {email_rec['email']} (active={email_rec['active']})")
    else:
        # Show active recipients
        cursor.execute("SELECT email FROM email_recipients WHERE active=1")
        active_emails = cursor.fetchall()
        print(f"   Active recipients:")
        for email_rec in active_emails:
            print(f"      ✅ {email_rec['email']}")
    
    # Check floor_events
    cursor.execute("SELECT COUNT(*) as cnt FROM floor_events")
    events_count = cursor.fetchone()["cnt"]
    print(f"   Floor events table: {events_count} detection records")
    
    if events_count > 0:
        # Show recent events
        cursor.execute("SELECT source, is_dirty, created_at FROM floor_events ORDER BY created_at DESC LIMIT 5")
        recent = cursor.fetchall()
        print(f"   Recent detections:")
        for event in recent:
            dirty_status = "🔴 DIRTY" if event['is_dirty'] else "🟢 CLEAN"
            print(f"      {event['source']} - {dirty_status} - {event['created_at']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Check YOLO model
print("\n[4/6] Checking YOLO model file...")
try:
    model_path = backend_dir / "computer_vision" / "models" / "best.pt"
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024*1024)
        print(f"✅ YOLO model found: {model_path}")
        print(f"   Size: {size_mb:.1f} MB")
    else:
        print(f"❌ YOLO model NOT found at: {model_path}")
        print(f"   Download trained model and place at that path")
except Exception as e:
    print(f"❌ Error checking model: {e}")

# 5. Test SMTP connection
print("\n[5/6] Testing SMTP connection...")
try:
    import ssl
    import smtplib
    
    print(f"   Attempting STARTTLS on {smtp_host}:{smtp_port}...")
    context = ssl.create_default_context()
    
    try:
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        print(f"   ✅ Connected to {smtp_host}:{smtp_port}")
        
        server.ehlo()
        print(f"   ✅ EHLO handshake OK")
        
        server.starttls(context=context)
        print(f"   ✅ STARTTLS OK")
        
        server.login(smtp_user, smtp_pass)
        print(f"   ✅ LOGIN OK")
        
        server.quit()
        print(f"✅ SMTP connection successful!")
        
    except Exception as e1:
        print(f"   ⚠️  STARTTLS failed: {e1}")
        print(f"   Trying SMTP_SSL fallback on port 465...")
        
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_host, 465, context=context, timeout=10)
            print(f"   ✅ Connected via SMTP_SSL")
            
            server.login(smtp_user, smtp_pass)
            print(f"   ✅ LOGIN OK")
            
            server.quit()
            print(f"✅ SMTP_SSL connection successful!")
            
        except Exception as e2:
            print(f"   ❌ SMTP_SSL also failed: {e2}")
            print(f"   TROUBLESHOOTING:")
            print(f"      1. Check SMTP_PASS is Gmail App Password (not regular password)")
            print(f"      2. If Gmail has 2FA, generate app password at: https://myaccount.google.com/apppasswords")
            print(f"      3. Check firewall allows SMTP port 587 or 465")
            print(f"      4. Check .env file for correct credentials")
            
except Exception as e:
    print(f"❌ SMTP test error: {e}")
    import traceback
    traceback.print_exc()

# 6. Summary and recommendations
print("\n[6/6] Summary and Recommendations")
print("=" * 70)

issues = []

if active_cam_count == 0:
    issues.append("❌ No active cameras - Add camera via frontend (Kelola Kamera)")

if active_email_count == 0:
    issues.append("❌ No active email recipients - Add email via frontend (Notifikasi Email)")

if not model_path.exists():
    issues.append("❌ YOLO model missing - Place trained model at computer_vision/models/best.pt")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ All checks passed! System should be working.")
    print("\nIf emails still not arriving:")
    print("   1. Check Gmail spam/promotions folder")
    print("   2. Mark email as 'Not Spam' in Gmail")
    print("   3. Check backend logs for SMTP errors")
    print("   4. Wait 60 seconds minimum between notifications (rate-limiting)")
    print("   5. Run: curl http://127.0.0.1:8000/email-recipients/test")

print("\n" + "=" * 70)
print("Next steps:")
print("   1. If issues found above: Fix them")
print("   2. Frontend → Add camera (Kelola Kamera)")
print("   3. Frontend → Add email recipient (Notifikasi Email)")
print("   4. Wait 5-30 seconds for monitor to detect dirty floor")
print("   5. Check Gmail inbox for notification email")
print("=" * 70)
