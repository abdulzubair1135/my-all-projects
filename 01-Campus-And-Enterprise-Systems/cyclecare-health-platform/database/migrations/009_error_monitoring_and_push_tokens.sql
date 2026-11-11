-- ==============================================================================
-- CycleCare Migration 009: Global Error Monitoring and Push Notification Tokens
-- Author: CycleCare Platform Architecture Team
-- ==============================================================================

-- 1. Global Application Error Monitoring Table
CREATE TABLE IF NOT EXISTS app_error_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL DEFAULT 'BACKEND', -- 'ANDROID', 'BACKEND', 'ADMIN'
    severity VARCHAR(20) NOT NULL DEFAULT 'ERROR', -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    message TEXT NOT NULL,
    stack TEXT,
    route VARCHAR(255),
    method VARCHAR(20),
    user_id UUID,
    status_code INTEGER,
    resolved BOOLEAN DEFAULT FALSE,
    device_info JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_app_error_logs_created_at ON app_error_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_error_logs_severity ON app_error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_app_error_logs_resolved ON app_error_logs(resolved);

-- 2. FCM Device Push Tokens Table
CREATE TABLE IF NOT EXISTS device_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token TEXT NOT NULL,
    platform VARCHAR(20) DEFAULT 'ANDROID',
    device_model VARCHAR(100),
    os_version VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, token)
);

CREATE INDEX IF NOT EXISTS idx_device_tokens_user ON device_tokens(user_id);
