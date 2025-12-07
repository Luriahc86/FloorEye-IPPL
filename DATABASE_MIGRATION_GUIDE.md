# 🔄 Database Migration: File-Based → Database-Only Image Storage

## Perubahan yang Dilakukan

Sistem telah diupdate untuk **hanya menyimpan gambar di database** (LONGBLOB), bukan di folder assets:

### Apa yang Berubah

| Aspek                | Sebelumnya                     | Sekarang                    |
| -------------------- | ------------------------------ | --------------------------- |
| Penyimpanan gambar   | File di `assets/saved_images/` | Database (LONGBLOB column)  |
| Kolom database       | `image_path` (path string)     | `image_data` (binary data)  |
| Ukuran folder assets | Bertambah setiap deteksi       | Tetap kecil                 |
| Backup               | File + Database                | Database saja               |
| Cleanup              | Manual hapus files             | Automatic saat delete event |

---

## Langkah Migrasi (Jika Sudah Ada Database Existing)

### Step 1: Backup Database (Penting!)

```bash
# Windows Command Prompt
mysqldump -u root floor_eye > floor_eye_backup.sql
```

### Step 2: Jalankan Migration Script

```bash
# Windows Command Prompt
cd D:\IPPL\FloorEye\Backend\store
mysql -u root floor_eye < migrate_to_db_images.sql
```

### Step 3: Verifikasi Migration

```bash
# Buka MySQL CLI
mysql -u root floor_eye

# Jalankan queries:
DESCRIBE floor_events;
SELECT COUNT(*) FROM floor_events WHERE image_data IS NOT NULL;
```

### Step 4: Update .env (jika perlu)

Tidak ada perubahan pada `.env`, sistem sudah kompatibel.

### Step 5: Restart Backend

```bash
# Stop backend yang sedang running
# Kemudian start ulang:
cd D:\IPPL\FloorEye\Backend
python -m uvicorn app:app --reload
```

---

## Database Schema Baru

### floor_events Table

```sql
CREATE TABLE floor_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,              -- "camera_1", "upload", etc
    is_dirty BOOLEAN NOT NULL,                -- 1=kotor, 0=bersih
    confidence FLOAT NULL,                    -- YOLO confidence score
    notes TEXT NULL,                          -- Notes/description
    image_data LONGBLOB NULL,                 -- ✅ Image binary data
    image_path TEXT NULL,                     -- (deprecated, for backward compat)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_created_at (created_at)
);
```

---

## Perubahan di Backend Routes

### `/detect/image` (Upload Image)

**Sebelumnya:**

```python
INSERT INTO floor_events (source, is_dirty, confidence, image_path)
VALUES ('upload', 1, 0.95, '/path/to/file.jpg')
```

**Sekarang:**

```python
INSERT INTO floor_events (source, is_dirty, confidence, image_data)
VALUES ('upload', 1, 0.95, <binary_data>)  # Binary image bytes
```

### `/detect/frame` (Deteksi dari Camera)

**Sama seperti `/detect/image`** - menyimpan ke `image_data` column.

### `/history` (Get Detection History)

**Sebelumnya:**

```json
{
  "id": 1,
  "is_dirty": true,
  "image_path": "/assets/saved_images/1.jpg"
}
```

**Sekarang:**

```json
{
  "id": 1,
  "is_dirty": true,
  "source": "camera_1"
}
```

(Gambar diakses via `/history/{id}/image` endpoint)

### `/history/{event_id}/image` (Get Image)

**Sebelumnya:**

```
Membaca file dari disk: /assets/saved_images/1.jpg
```

**Sekarang:**

```
Membaca dari database: SELECT image_data FROM floor_events WHERE id={event_id}
```

### `/image/{event_id}` (Convenience Endpoint)

**Sama seperti `/history/{event_id}/image`** - ambil dari database.

---

## Perubahan di Backend Services

### Monitor Service

- ✅ Encode frame ke JPEG bytes
- ✅ Insert bytes ke `image_data` column
- ✅ Tidak lagi save file ke assets folder

```python
# Sebelumnya
INSERT INTO floor_events (source, image_path) VALUES ('camera_1', '/path/to/file')

# Sekarang
_, frame_bytes = cv2.imencode('.jpg', frame)
INSERT INTO floor_events (source, image_data) VALUES ('camera_1', frame_bytes)
```

---

## Keuntungan Sistem Baru

✅ **Tidak ada file di disk** - lebih rapi  
✅ **Backup mudah** - hanya backup database  
✅ **Skalabilitas** - database handle besar data  
✅ **Keamanan** - Tidak ada file path exposure  
✅ **Cleanup otomatis** - Hapus event = hapus gambar  
✅ **Consistency** - Event & gambar dalam satu transaksi

---

## Konfigurasi MySQL untuk LONGBLOB

Pastikan MySQL dikonfigurasi untuk handle LONGBLOB:

```sql
-- Cek max_allowed_packet (default 4MB, bisa jadi terlalu kecil)
SHOW VARIABLES LIKE 'max_allowed_packet';

-- Jika perlu diperbesar (edit my.ini / my.cnf):
max_allowed_packet=256M
```

---

## Frontend - Tidak ada perubahan

Frontend tidak perlu update - endpoint masih sama:

- `GET /history` → list events
- `GET /history/{id}/image` → fetch image
- `POST /detect/image` → detect dari upload
- `POST /detect/frame` → detect dari camera

Frontend terus bisa menampilkan gambar: `<img src="/history/{id}/image" />`

---

## Rollback (Jika Diperlukan)

Jika perlu kembali ke sistem berbasis file:

```bash
# 1. Restore backup
mysql -u root floor_eye < floor_eye_backup.sql

# 2. Update code kembali ke branch sebelumnya
git checkout main -- Backend/routes/ Backend/services/

# 3. Restart
```

---

## Troubleshooting

### Error: "Packet too large"

```
Solusi: Perbesar max_allowed_packet di MySQL config
```

### Error: "Column 'image_data' doesn't exist"

```
Solusi: Jalankan migration script:
mysql -u root floor_eye < migrate_to_db_images.sql
```

### Gambar tidak muncul di history

```
Solusi: Pastikan image_data tersimpan (bukan image_path yang kosong)
SELECT * FROM floor_events WHERE id=1\G
```

---

## Verifikasi Berhasil

```bash
# 1. Check database schema
mysql -u root floor_eye -e "DESCRIBE floor_events;"

# 2. Check ada image_data
mysql -u root floor_eye -e "SELECT COUNT(*) FROM floor_events WHERE image_data IS NOT NULL;"

# 3. Test backend
curl http://127.0.0.1:8000/health

# 4. Test history
curl http://127.0.0.1:8000/history

# 5. Test fetch image
curl http://127.0.0.1:8000/history/1/image -o test.jpg
```

---

## Summary

✅ Database schema updated  
✅ Backend routes updated  
✅ Monitor service updated  
✅ History routes updated  
✅ App endpoints updated

**Sistem sekarang menggunakan database-only storage untuk gambar deteksi!** 🎉

Untuk migrasi database existing, jalankan:

```bash
mysql -u root floor_eye < Backend/store/migrate_to_db_images.sql
```
