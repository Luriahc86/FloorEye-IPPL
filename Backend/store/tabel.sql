DROP DATABASE IF EXISTS floor_eye;
CREATE DATABASE floor_eye;
USE floor_eye;

-- ================================
-- TABLE: floor_events (riwayat deteksi)
-- ================================
CREATE TABLE floor_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    is_dirty BOOLEAN NOT NULL,
    confidence FLOAT NULL,
    notes TEXT NULL,
    image_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- TABLE: cameras (CCTV/RTSP)
-- ================================
CREATE TABLE cameras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    lokasi VARCHAR(255) NULL,
    link TEXT NOT NULL,
    aktif BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- TABLE: email_recipients
-- Untuk notifikasi Gmail via SMTP
-- ================================
CREATE TABLE email_recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);