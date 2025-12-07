# 🎥 Live Camera Real-Time Detection - Feature Guide

## ✨ Fitur Baru: Auto-Deteksi Real-Time

Anda sekarang dapat menjalankan **deteksi otomatis real-time** langsung dari Live Camera di frontend!

### 🎯 Apa yang Bisa Dilakukan

1. **Aktifkan Kamera** → Mulai streaming live dari webcam/camera
2. **Deteksi Manual** → Klik "Deteksi Sekarang" untuk single shot detection
3. **Auto-Deteksi** → Klik "▶️ Auto-Deteksi" untuk deteksi otomatis setiap 5 detik
4. **Lihat Hasil Real-Time** → Status BERSIH/KOTOR ditampilkan langsung
5. **Riwayat 10 Deteksi Terakhir** → Lihat history deteksi dalam notifikasi

---

## 🚀 Cara Menggunakan

### Step 1: Buka Live Camera Page

```
Frontend: http://127.0.0.1:5173
Menu: 📹 Live Camera
```

### Step 2: Aktifkan Kamera

- Klik tombol **"Aktifkan Kamera"**
- Berikan akses kamera ketika browser meminta

### Step 3: Jalankan Deteksi

#### Opsi A: Manual (Single Shot)

```
Klik: "Deteksi Sekarang"
Tunggu: Hasil muncul dalam 1-2 detik
```

#### Opsi B: Auto-Deteksi (Recommended!)

```
Klik: "▶️ Auto-Deteksi"
Sistem akan:
  - Deteksi setiap 5 detik otomatis
  - Tampilkan status BERSIH/KOTOR live
  - Simpan history 10 deteksi terakhir
  - Tunjukkan confidence score
```

### Step 4: Monitor Status

**Visual Indicators:**

- 🟢 **LANTAI BERSIH** (hijau) = Confidence rendah/tidak ada deteksi
- 🔴 **KOTOR TERDETEKSI** (merah) = Dirty floor detected + confidence score
- ⏱️ **Auto-deteksi berjalan** = Indicator saat auto-detect aktif

### Step 5: Cek Riwayat

```
Section: 📊 Riwayat Deteksi (10 Terakhir)
Lihat: Timestamp + status + confidence setiap deteksi
Scroll: Max height dengan scroll bar
```

---

## 📊 Informasi yang Ditampilkan

Setiap deteksi menampilkan:

| Field           | Deskripsi                             |
| --------------- | ------------------------------------- |
| **Status**      | 🚨 KOTOR atau ✅ BERSIH               |
| **Confidence**  | 0-100% (semakin tinggi = lebih pasti) |
| **Event ID**    | ID unik di database                   |
| **Waktu**       | Timestamp deteksi                     |
| **Auto-Detect** | Indicator bahwa sistem berjalan       |

---

## 🔄 Deteksi Otomatis vs Manual

| Fitur        | Otomatis              | Manual                |
| ------------ | --------------------- | --------------------- |
| **Interval** | Setiap 5 detik        | Per-click             |
| **Use Case** | Monitoring 24/7       | Verifikasi manual     |
| **Riwayat**  | 10 deteksi terakhir   | Deteksi terakhir saja |
| **CPU**      | Normal                | Single spike          |
| **Best For** | Background monitoring | Quick check           |

---

## 💡 Tips Penggunaan

### Untuk Monitoring Kontinyu

1. Aktifkan kamera
2. Klik "▶️ Auto-Deteksi"
3. Biarkan berjalan di background
4. Monitor riwayat deteksi

### Untuk Verifikasi Cepat

1. Aktifkan kamera
2. Klik "Deteksi Sekarang" saja
3. Lihat hasil sekali

### Untuk Testing YOLO Model

1. Buat kondisi kotor di lantai
2. Aktifkan auto-deteksi
3. Lihat confidence score meningkat
4. Gunakan untuk fine-tune model

---

## 🔧 Konfigurasi

### Mengubah Interval Auto-Deteksi

Edit `Frontend/src/pages/LiveCameraPage.tsx`:

```tsx
<CameraViewer
  onResult={handleDetectionResult}
  autoDetectInterval={5000}  // Default 5 detik
/>

// Ubah ke:
autoDetectInterval={3000}  // 3 detik
autoDetectInterval={10000} // 10 detik
```

### Backend Endpoint

```
POST /detect/frame
Content-Type: application/json

Request:
{
  "image_base64": "...",  // Base64 image dari canvas
  "notes": "live-camera-auto-detect"
}

Response:
{
  "id": 123,
  "is_dirty": true,
  "confidence": 0.85,
  "created_at": "2025-12-07T10:30:45.123456",
  "source": "camera",
  "notes": "live-camera-auto-detect"
}
```

---

## 🐛 Troubleshooting

### Kamera Tidak Bisa Diakses

```
Error: "Tidak dapat mengakses kamera"
Solution:
1. Izinkan akses kamera di browser
2. Cek Settings → Privacy → Camera
3. Restart browser jika perlu
```

### Deteksi Selalu "BERSIH"

```
Kemungkinan:
1. YOLO model belum terlatih untuk deteksi lantai kotor
2. Confidence threshold terlalu tinggi
3. Format gambar tidak sesuai
Solution:
- Cek training data YOLO
- Test dengan /detect/image endpoint
```

### Auto-Deteksi Tidak Berjalan

```
Check:
1. Backend running di port 8000
2. Network tab di browser console
3. Cek CORS settings di app.py
```

---

## 📈 Performance

| Metrik                | Nilai                 |
| --------------------- | --------------------- |
| **Deteksi per detik** | 1 per 5 detik (auto)  |
| **Latency**           | 1-2 detik per deteksi |
| **CPU Usage**         | ~20-30% (moderate)    |
| **Memory**            | ~100-200 MB           |
| **Bandwidth**         | Minimal (lokal saja)  |

---

## 🎓 Integrasi dengan Monitor Thread

**Live Camera** (Frontend):

- Deteksi real-time dari webcam
- Manual trigger per click
- Hasil ditampilkan immediately

**Monitor Thread** (Backend):

- Polling RTSP cameras setiap 5 detik
- Automatic email notification
- Rate-limiting 60 sec per camera

**Keduanya independen**, dapat berjalan bersamaan!

---

## ✅ Checklist untuk Testing

- [ ] Kamera dapat diakses (green indicator)
- [ ] Tombol "Deteksi Sekarang" responsive
- [ ] Auto-deteksi dapat dinyalakan/dimatikan
- [ ] Status BERSIH/KOTOR berubah sesuai kondisi lantai
- [ ] Confidence score ditampilkan dengan benar
- [ ] Riwayat deteksi terupdate otomatis
- [ ] Video stream smooth tanpa lag
- [ ] Event tersimpan di database

---

## 📞 Need Help?

Lihat dokumentasi lengkap:

- `README.md` - Overview sistem
- `EMAIL_NOTIFICATION_GUIDE.md` - Setup lengkap
- Backend logs untuk debug deteksi

---

**Happy detecting!** 🎥✨
