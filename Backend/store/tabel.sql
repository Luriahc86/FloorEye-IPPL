DROP DATABASE IF EXISTS floor_eye;
CREATE DATABASE floor_eye
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE floor_eye;

CREATE TABLE floor_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    is_dirty BOOLEAN NOT NULL,
    confidence FLOAT NULL,
    notes TEXT NULL,
    image_data LONGBLOB NULL,
    image_path TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_source (source),
    INDEX idx_created_at (created_at),
    INDEX idx_is_dirty (is_dirty)
) ENGINE=InnoDB;

CREATE TABLE email_recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_active (active)
) ENGINE=InnoDB;
