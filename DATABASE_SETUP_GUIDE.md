# 🚀 Database Fix - Setup Guide

Sistem telah diupdate untuk **menyimpan gambar hanya di database** (bukan di asset folder).

---

## ⚡ Quick Setup (2 menit)

### Step 1: Setup Database

```bash
cd D:\IPPL\FloorEye\Backend
setup_database.bat
```

Script ini akan:

- ✅ Buat database baru jika belum ada
- ✅ Atau migrate database existing (dengan backup otomatis)
- ✅ Verify semua schema sudah benar

### Step 2: Restart Backend

```bash
cd D:\IPPL\FloorEye\Backend
python -m uvicorn app:app --reload
```

### Step 3: Use Frontend

```
Open: http://127.0.0.1:5173
```

Done! ✅

---

## 📋 Apa yang Berubah

### Database

| Kolom        | Sebelumnya          | Sekarang                   |
| ------------ | ------------------- | -------------------------- |
| `image_path` | String path ke file | NULL (deprecated)          |
| `image_data` | (tidak ada)         | LONGBLOB - gambar langsung |

### Penyimpanan Gambar

| Aspek   | Sebelumnya                   | Sekarang        |
| ------- | ---------------------------- | --------------- |
| Lokasi  | `/assets/saved_images/*.jpg` | Database        |
| Size    | Folder terus bertambah       | Database handle |
| Backup  | File + DB                    | DB saja         |
| Cleanup | Manual                       | Automatic       |

### Deteksi

```python
# Sebelumnya
frame_file = f"/assets/saved_images/{event_id}.jpg"
cv2.imwrite(frame_file, frame)
INSERT INTO floor_events (image_path) VALUES (frame_file)

# Sekarang
_, frame_bytes = cv2.imencode('.jpg', frame)
INSERT INTO floor_events (image_data) VALUES (frame_bytes)
```

### History/Image View

```javascript
// Sebelumnya
fetch(`/history/1`)  // Returns image_path
<img src={event.image_path} />

// Sekarang
fetch(`/history/1/image`)  // Returns image bytes
<img src="/history/1/image" />
```

---

## 📊 Verifikasi Setup

### Check 1: Database Terbuat

```bash
mysql -u root floor_eye -e "SHOW TABLES;"
```

Should show:

```
+----------------------+
| Tables_in_floor_eye  |
+----------------------+
| cameras              |
| email_recipients     |
| floor_events         |
+----------------------+
```

### Check 2: Schema Benar

```bash
mysql -u root floor_eye -e "DESCRIBE floor_events;"
```

Should show column `image_data` dengan type `longblob`.

### Check 3: API Response

```bash
curl http://127.0.0.1:8000/health
# Should return: {"status": "healthy"}

curl http://127.0.0.1:8000/history
# Should return JSON list of events
```

---

## 🧪 Test Detection & Storage

### Test 1: Upload Image

1. Open http://127.0.0.1:5173
2. Go to **Upload** page
3. Upload image (or use test image)
4. Click detect
5. Should show result

### Test 2: Verify Image Stored in DB

```bash
mysql -u root floor_eye -e "SELECT id, is_dirty, image_data IS NOT NULL as has_image FROM floor_events LIMIT 5;"
```

Should show:

```
+----+---------+------------------+
| id | is_dirty | has_image        |
+----+---------+------------------+
|  1 |        1 |                1 |
+----+---------+------------------+
```

(Column `has_image` should be 1 = true)

### Test 3: Fetch Image

```bash
# Get image from event_id=1
curl http://127.0.0.1:8000/history/1/image -o test.jpg

# Open test.jpg to verify
```

---

## 🔄 Migrasi dari Sistem Lama

Jika punya database existing dengan `image_path`:

### Opsi 1: Automatic (Recommended)

```bash
cd D:\IPPL\FloorEye\Backend
setup_database.bat
```

- Otomatis detect database existing
- Buat backup dengan timestamp
- Jalankan migration
- Verify schema

### Opsi 2: Manual

```bash
# Backup
mysqldump -u root floor_eye > backup.sql

# Migrate
cd D:\IPPL\FloorEye\Backend\store
mysql -u root floor_eye < migrate_to_db_images.sql

# Verify
mysql -u root floor_eye -e "DESCRIBE floor_events;"
```

---

## 🔧 Troubleshooting

### Error: "Can't connect to MySQL server"

```
Solution:
1. Check MySQL running (Laragon)
2. Check port 3306 is accessible
3. Try: mysql -u root
```

### Error: "Access denied for user 'root'"

```
Solution:
1. Check password in .env (should be empty for Laragon)
2. Try: mysql -u root -p (then press Enter for empty password)
```

### Error: "Packet too large"

```
Solution:
Edit MySQL config (my.ini or my.cnf):
max_allowed_packet=256M

Then restart MySQL
```

### Image not showing in history

```
Solution:
Check if image_data stored:
SELECT COUNT(*) FROM floor_events WHERE image_data IS NOT NULL;

Should return > 0
```

---

## 📖 File Referensi

| File                             | Untuk                     |
| -------------------------------- | ------------------------- |
| `setup_database.bat`             | Database setup otomatis   |
| `store/tabel.sql`                | Fresh schema              |
| `store/migrate_to_db_images.sql` | Migration dari old system |
| `DATABASE_MIGRATION_GUIDE.md`    | Detailed migration docs   |
| `DATABASE_FIX_SUMMARY.md`        | Ringkasan perubahan       |

---

## ✅ Checklist

- [ ] Jalankan `setup_database.bat`
- [ ] Check database terbuat: `mysql -u root floor_eye -e "SHOW TABLES;"`
- [ ] Check schema: `mysql -u root floor_eye -e "DESCRIBE floor_events;"`
- [ ] Restart backend
- [ ] Test upload image
- [ ] Verify image stored: `mysql -u root floor_eye -e "SELECT COUNT(*) FROM floor_events WHERE image_data IS NOT NULL;"`
- [ ] Test fetch image: `curl http://127.0.0.1:8000/history/1/image`
- [ ] Check history view shows images

---

## 🎉 Success Indicators

✅ Database created/migrated  
✅ `image_data` column exists  
✅ Upload image works  
✅ Image shows in history  
✅ No `assets/saved_images/` folder growing

---

## 📞 Support

- **Setup issue?** → Check `setup_database.bat` output
- **Schema issue?** → Check `DESCRIBE floor_events;`
- **Image storage issue?** → Check `image_data` column has data
- **Migration issue?** → Use `floor_eye_backup_*.sql` to restore

---

**Next:** Run `setup_database.bat` and you're done! 🚀
