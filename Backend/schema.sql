-- Active: 1765519306496@@trolley.proxy.rlwy.net@28263@railway
DROP TABLE IF EXISTS email_recipients;
DROP TABLE IF EXISTS floor_events;
CREATE TABLE IF NOT EXISTS email_recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS floor_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    is_dirty TINYINT(1) NOT NULL,
    confidence FLOAT,
    notes TEXT,
    image_data LONGBLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_email_recipients_active ON email_recipients(active);
CREATE INDEX idx_floor_events_created_at ON floor_events(created_at);
