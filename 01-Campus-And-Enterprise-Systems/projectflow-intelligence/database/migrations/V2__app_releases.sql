-- ==============================================================================
-- PROJECTFLOW INTELLIGENCE — V2 APP RELEASES MIGRATION
-- Table for managing official Android & Desktop application distribution artifacts
-- ==============================================================================

CREATE TABLE IF NOT EXISTS app_releases (
    id UUID PRIMARY KEY,
    application_id VARCHAR(100) NOT NULL DEFAULT 'com.projectflow.android',
    version_name VARCHAR(50) NOT NULL,
    version_code BIGINT NOT NULL,
    artifact_filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'application/vnd.android.package-archive',
    file_size_bytes BIGINT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL,
    release_channel VARCHAR(50) NOT NULL DEFAULT 'STABLE',
    release_notes TEXT,
    minimum_supported_version_code BIGINT DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'PUBLISHED',
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_app_version UNIQUE (application_id, version_code),
    CONSTRAINT chk_release_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED', 'DEPRECATED')),
    CONSTRAINT chk_release_channel CHECK (release_channel IN ('STABLE', 'BETA', 'NIGHTLY'))
);

CREATE INDEX IF NOT EXISTS idx_releases_app_status ON app_releases(application_id, status);
CREATE INDEX IF NOT EXISTS idx_releases_published_at ON app_releases(published_at DESC);
