# FloorEye - Dokumentasi Sistem

## 📋 Daftar Isi

1. [Gambaran Umum](#gambaran-umum)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Struktur File](#struktur-file)
4. [Hubungan Antar File](#hubungan-antar-file)
5. [Alur Kerja Sistem](#alur-kerja-sistem)
6. [Environment Variables](#environment-variables)
7. [Batasan Sistem](#batasan-sistem)
8. [Cara Menggunakan Sistem](#cara-menggunakan-sistem)

---

## Gambaran Umum

**FloorEye** adalah sistem deteksi kebersihan lantai berbasis AI yang menggunakan teknologi computer vision (YOLO) untuk mendeteksi apakah lantai dalam kondisi bersih atau kotor secara real-time.

### Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Frontend | React + TypeScript + Vite + TailwindCSS |
| Backend | Python + FastAPI |
| ML Service | Python + FastAPI + YOLOv8 (Ultralytics) |
| Database | MySQL |
| Email Service | Resend API |
| Deployment | Vercel (Frontend), Railway (Backend), HuggingFace Spaces (ML) |

---

## Arsitektur Sistem

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │     Backend     │     │   ML Service    │
│    (Vercel)     │────▶│   (Railway)     │────▶│ (HuggingFace)   │
│                 │     │                 │     │                 │
│  React + Vite   │     │    FastAPI      │     │  FastAPI + YOLO │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼─────┐           ┌───────▼───────┐
              │  MySQL    │           │  Resend API   │
              │ (Railway) │           │   (Email)     │
              └───────────┘           └───────────────┘
```

### Pembagian Tanggung Jawab

| Service | Tanggung Jawab |
|---------|----------------|
| **Frontend** | UI/UX, akses kamera, menampilkan hasil deteksi |
| **Backend** | API gateway, menyimpan history, mengirim email notifikasi |
| **ML Service** | Menjalankan model YOLO untuk deteksi objek |
| **Database** | Menyimpan history deteksi dan daftar penerima email |
| **Resend API** | Mengirim email notifikasi |

---

## Struktur File

### Backend (`/Backend`)

```
Backend/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Entry point FastAPI application
│   ├── routes/
│   │   ├── __init__.py       # Routes initialization
│   │   ├── detection.py      # Endpoint deteksi lantai (/detect/frame)
│   │   ├── email_recipients.py # Endpoint kelola penerima email
│   │   ├── health.py         # Endpoint health check
│   │   ├── history.py        # Endpoint riwayat deteksi
│   │   └── db_test.py        # Endpoint test koneksi database
│   ├── services/
│   │   ├── __init__.py       # Services initialization
│   │   ├── emailer.py        # Service pengiriman email via Resend API
│   │   ├── detector.py       # Service helper untuk deteksi
│   │   └── monitor.py        # Service monitoring background
│   ├── store/
│   │   ├── __init__.py       # Store initialization
│   │   ├── db.py             # Koneksi database dan helper
│   │   └── database.py       # Konfigurasi SQLAlchemy
│   └── utils/
│       ├── __init__.py       # Utils initialization
│       ├── config.py         # Konfigurasi environment variables
│       └── logging.py        # Konfigurasi logging
├── .env.example              # Contoh environment variables
├── Dockerfile                # Docker configuration
├── Procfile                  # Railway deployment config
├── requirements.txt          # Python dependencies
├── schema.sql                # Struktur tabel database
└── validate_separation.py    # Script validasi arsitektur
```

### Frontend (`/Frontend`)

```
Frontend/
├── src/
│   ├── main.tsx              # Entry point React application
│   ├── index.css             # Global styles
│   ├── App.css               # App component styles
│   ├── components/
│   │   ├── CameraViewer.tsx  # Komponen kamera dan deteksi
│   │   ├── HistoryItem.tsx   # Komponen item riwayat
│   │   ├── Navbar.tsx        # Komponen navigasi atas
│   │   └── Sidebar.tsx       # Komponen sidebar navigasi
│   ├── pages/
│   │   ├── LiveCameraPage.tsx      # Halaman kamera live
│   │   ├── HistoryPage.tsx         # Halaman riwayat deteksi
│   │   └── NotificationsPage.tsx   # Halaman pengaturan notifikasi
│   ├── layouts/
│   │   └── MainLayout.tsx    # Layout utama dengan sidebar
│   ├── router/
│   │   └── index.tsx         # Konfigurasi routing
│   ├── services/
│   │   ├── api.ts            # Axios instance dan konfigurasi
│   │   ├── detection.service.ts    # Service deteksi
│   │   ├── email.service.ts        # Service email
│   │   ├── emailRecipients.service.ts # Service penerima email
│   │   └── history.service.ts      # Service riwayat
│   └── utils/
│       └── config.ts         # Konfigurasi frontend
├── .env.example              # Contoh environment variables
├── .env.production           # Environment untuk production
├── index.html                # HTML entry point
├── package.json              # Node.js dependencies
├── tailwind.config.js        # Konfigurasi TailwindCSS
├── vite.config.ts            # Konfigurasi Vite
└── vercel.json               # Konfigurasi deployment Vercel
```

### ML Service (`/ml_service`)

```
ml_service/
├── app.py                    # Entry point ML service
├── models/
│   └── yolov8n.pt           # Model YOLO (tidak di-commit, download saat deploy)
├── .env.example              # Contoh environment variables
├── Dockerfile                # Docker configuration untuk HuggingFace
├── requirements.txt          # Python dependencies
└── README.md                 # Dokumentasi ML service
```

---

## Hubungan Antar File

### Backend

```
main.py
├── routes/__init__.py (mendaftarkan semua router)
│   ├── detection.py ──────┬──▶ services/emailer.py (kirim notifikasi)
│   │                      └──▶ store/db.py (simpan ke database)
│   ├── email_recipients.py ──▶ store/db.py
│   ├── history.py ───────────▶ store/db.py
│   └── health.py
├── utils/config.py (konfigurasi global)
└── utils/logging.py (konfigurasi log)
```

### Frontend

```
main.tsx
├── router/index.tsx (routing)
│   ├── layouts/MainLayout.tsx
│   │   ├── components/Navbar.tsx
│   │   └── components/Sidebar.tsx
│   └── pages/
│       ├── LiveCameraPage.tsx
│       │   └── components/CameraViewer.tsx
│       │       └── services/api.ts ──▶ Backend API
│       ├── HistoryPage.tsx
│       │   ├── components/HistoryItem.tsx
│       │   └── services/history.service.ts
│       └── NotificationsPage.tsx
│           └── services/emailRecipients.service.ts
└── services/api.ts (Axios instance shared)
```

### Komunikasi Antar Service

```
┌──────────────────────────────────────────────────────────────────┐
│                         ALUR DATA                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [CameraViewer.tsx] ─── POST /detect/frame ───▶ [detection.py]   │
│                                                       │           │
│                                                       ▼           │
│                                               [YOLO_SERVICE_URL]  │
│                                               (HuggingFace ML)    │
│                                                       │           │
│                                                       ▼           │
│  [detection.py] ◀─────── hasil deteksi ──────────────┘           │
│         │                                                         │
│         ├── simpan ke database (store/db.py)                      │
│         └── kirim email jika kotor (services/emailer.py)         │
│                        │                                          │
│                        ▼                                          │
│                  [Resend API] ──▶ Email ke penerima              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Alur Kerja Sistem

### 1. Alur Deteksi Lantai (Real-time)

```
1. User membuka halaman Live Camera
2. Browser meminta akses kamera
3. Kamera mulai streaming video
4. Setiap 60 detik (auto-detect):
   a. Frontend capture frame dari video
   b. Frame dikirim ke Backend (POST /detect/frame)
   c. Backend forward frame ke ML Service (HuggingFace)
   d. ML Service menjalankan model YOLO
   e. Hasil deteksi dikembalikan ke Backend
   f. Backend:
      - Menyimpan hasil ke database
      - Jika lantai kotor: kirim email notifikasi
   g. Frontend menampilkan hasil deteksi
```

### 2. Alur Notifikasi Email

```
1. Deteksi menemukan lantai kotor (is_dirty = true)
2. Backend mengambil daftar email aktif dari database
3. Backend mengirim email via Resend API
4. Penerima menerima email notifikasi
```

### 3. Alur Melihat Riwayat

```
1. User membuka halaman History
2. Frontend request ke Backend (GET /history)
3. Backend query database
4. Data dikembalikan dan ditampilkan
```

### 4. Alur Kelola Penerima Email

```
1. User membuka halaman Notifications
2. Frontend request daftar penerima (GET /email-recipients)
3. User dapat:
   - Menambah penerima baru (POST /email-recipients)
   - Mengaktifkan/menonaktifkan (PATCH /email-recipients/{id})
   - Menghapus penerima (DELETE /email-recipients/{id})
   - Test kirim email (GET /email-recipients/test)
```

---

## Environment Variables

### Backend (Railway)

| Variable | Deskripsi | Wajib |
|----------|-----------|-------|
| `DB_HOST` | Host database MySQL | Ya |
| `DB_PORT` | Port database (default: 3306) | Ya |
| `DB_USER` | Username database | Ya |
| `DB_PASSWORD` | Password database | Ya |
| `DB_NAME` | Nama database | Ya |
| `YOLO_SERVICE_URL` | URL endpoint ML service di HuggingFace | Ya |
| `RESEND_API_KEY` | API key dari Resend untuk email | Ya |
| `EMAIL_FROM` | Alamat pengirim email | Ya |
| `ENABLE_MONITOR` | Aktifkan background monitor (0/1) | Tidak |
| `CONF_THRESHOLD` | Threshold confidence deteksi (0.0-1.0) | Tidak |
| `NOTIFY_INTERVAL` | Interval notifikasi dalam detik | Tidak |

### Frontend (Vercel)

| Variable | Deskripsi | Wajib |
|----------|-----------|-------|
| `VITE_API_BASE` | Base URL backend API (HTTPS, tanpa trailing slash) | Ya |

### ML Service (HuggingFace)

| Variable | Deskripsi | Wajib |
|----------|-----------|-------|
| `MODEL_PATH` | Path ke file model YOLO | Tidak |
| `CONF_THRESHOLD` | Threshold confidence deteksi | Tidak |

---

## Batasan Sistem

### 1. Batasan Teknis

| Batasan | Deskripsi |
|---------|-----------|
| **Browser Support** | Hanya browser modern yang mendukung WebRTC (Chrome, Firefox, Edge, Safari) |
| **HTTPS Required** | Frontend dan Backend harus menggunakan HTTPS |
| **Kamera** | Memerlukan izin akses kamera dari browser |
| **Model YOLO** | Menggunakan model yang sudah di-train khusus untuk deteksi kotoran lantai |

### 2. Batasan Email (Resend Sandbox Mode)

| Batasan | Deskripsi |
|---------|-----------|
| **Penerima Terbatas** | Dengan sandbox mode, email hanya bisa dikirim ke email yang terdaftar di akun Resend |
| **Kuota Gratis** | 3,000 email/bulan pada tier gratis |
| **Domain Verification** | Untuk mengirim ke semua email, diperlukan verifikasi domain |

### 3. Batasan Performa

| Batasan | Deskripsi |
|---------|-----------|
| **Interval Deteksi** | Minimal 60 detik untuk menghindari spam email |
| **Ukuran Frame** | Frame gambar dikompresi sebelum dikirim |
| **Cold Start** | HuggingFace Spaces bisa lambat saat cold start (~30 detik) |

### 4. Batasan Infrastructure

| Batasan | Deskripsi |
|---------|-----------|
| **Railway Free Tier** | Terbatas pada resource tertentu |
| **Vercel Free Tier** | Bandwidth terbatas |
| **HuggingFace Free** | CPU only, bisa lambat untuk inferensi |

---

## Cara Menggunakan Sistem

### 1. Akses Aplikasi

Buka URL frontend yang sudah di-deploy di Vercel melalui browser.

### 2. Halaman Live Camera

1. **Izinkan akses kamera** saat browser meminta permission
2. Pastikan kamera mengarah ke lantai
3. Klik tombol **"▶️ Auto-Deteksi"** untuk memulai deteksi otomatis
4. Sistem akan:
   - Mendeteksi setiap 60 detik
   - Menampilkan status (Bersih/Kotor)
   - Menampilkan confidence level
5. Klik tombol lagi untuk menghentikan auto-deteksi

### 3. Halaman History

1. Klik menu **"History"** di sidebar
2. Lihat daftar riwayat deteksi
3. Setiap item menampilkan:
   - Waktu deteksi
   - Status (Bersih/Kotor)
   - Gambar (jika tersedia)
   - Confidence level

### 4. Halaman Notifications

1. Klik menu **"Notifikasi"** di sidebar
2. **Menambah penerima email:**
   - Masukkan alamat email
   - Klik tombol "Tambah"
3. **Mengaktifkan/menonaktifkan:**
   - Toggle switch di sebelah email
4. **Menghapus penerima:**
   - Klik tombol hapus
5. **Test email:**
   - Klik tombol "Test Email"
   - Periksa inbox email

### 5. Menerima Notifikasi

Ketika sistem mendeteksi lantai kotor:
1. Email otomatis dikirim ke semua penerima aktif
2. Subject: "🚨 [FloorEye] Lantai Kotor Terdeteksi!"
3. Body berisi informasi confidence level

---

## Troubleshooting

### Kamera Tidak Terdeteksi

1. Pastikan browser mendukung WebRTC
2. Izinkan akses kamera di browser settings
3. Gunakan HTTPS (bukan HTTP)

### Email Tidak Terkirim

1. Pastikan `RESEND_API_KEY` sudah di-set
2. Pastikan `EMAIL_FROM` menggunakan format yang benar
3. Dengan sandbox mode, pastikan penerima adalah email yang terdaftar di Resend

### Deteksi Lambat

1. HuggingFace Spaces bisa cold start (~30 detik)
2. Tunggu beberapa saat dan coba lagi

### Error Mixed Content

1. Pastikan `VITE_API_BASE` menggunakan HTTPS
2. Pastikan tidak ada trailing slash

---

## Kontak & Support

Jika mengalami masalah, silakan buat issue di repository GitHub atau hubungi tim pengembang.
