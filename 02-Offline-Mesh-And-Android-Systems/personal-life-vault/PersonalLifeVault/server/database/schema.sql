-- Personal Life Vault SQLite Database Schema

PRAGMA foreign_keys = ON;

-- Registered Sync Devices
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL UNIQUE,
    device_name TEXT,
    auth_token_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    last_seen INTEGER
);

CREATE INDEX IF NOT EXISTS idx_devices_id ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_token_hash ON devices(auth_token_hash);

-- Captured Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_event_id TEXT UNIQUE,
    device_id TEXT,
    app_name TEXT NOT NULL,
    title TEXT,
    content TEXT,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_notifications_client_event ON notifications(client_event_id);

-- Telecom Logs (SMS / Calls)
CREATE TABLE IF NOT EXISTS telecom_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_event_id TEXT UNIQUE,
    device_id TEXT,
    type TEXT NOT NULL, -- 'sms' | 'call'
    party TEXT,
    body TEXT,
    duration INTEGER,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_telecom_timestamp ON telecom_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_telecom_type_timestamp ON telecom_logs(type, timestamp);
CREATE INDEX IF NOT EXISTS idx_telecom_client_event ON telecom_logs(client_event_id);

-- Sensor / Telemetry Logs (steps, battery, user-controlled location)
CREATE TABLE IF NOT EXISTS sensor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_event_id TEXT UNIQUE,
    device_id TEXT,
    type TEXT NOT NULL, -- 'steps' | 'battery' | 'location'
    payload_json TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_type_timestamp ON sensor_logs(type, timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_client_event ON sensor_logs(client_event_id);

-- Vault Media Files (Photos, Audio, Documents)
CREATE TABLE IF NOT EXISTS media_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_event_id TEXT UNIQUE,
    device_id TEXT,
    original_name TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE, -- SHA-256 for physical deduplication
    local_path TEXT NOT NULL,
    mime_type TEXT,
    file_size INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_media_timestamp ON media_files(timestamp);
CREATE INDEX IF NOT EXISTS idx_media_file_hash ON media_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_media_client_event ON media_files(client_event_id);

-- Remote Device Commands (On-Demand File Backup & Storage Exploration)
CREATE TABLE IF NOT EXISTS device_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    command_type TEXT NOT NULL, -- 'EXPLORE_DIR' | 'BACKUP_FILE'
    payload TEXT NOT NULL,      -- JSON payload e.g. {"path": "/storage/emulated/0/DCIM"}
    status TEXT NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
    result TEXT,                 -- JSON result payload
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_device_commands_device_status ON device_commands(device_id, status);

