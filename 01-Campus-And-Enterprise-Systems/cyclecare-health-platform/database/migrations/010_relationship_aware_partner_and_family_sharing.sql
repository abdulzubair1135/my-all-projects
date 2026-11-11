-- Migration 010: Relationship-Aware Partner & Family Sharing System
-- CycleCare Product Enhancement:
-- Multi-member family sharing, relationship perspective tagging, granular revocable permissions,
-- and security audit trail.

-- 1. Extend relationship check constraint on partner_connections to include Daughter, Son
ALTER TABLE partner_connections 
DROP CONSTRAINT IF EXISTS partner_connections_relationship_check;

ALTER TABLE partner_connections
ADD CONSTRAINT partner_connections_relationship_check 
CHECK (relationship IN (
    'Mother', 'Father', 'Husband', 'Wife', 'Boyfriend', 'Girlfriend',
    'Daughter', 'Son', 'Best Friend', 'Sister', 'Brother', 'Family',
    'Guardian', 'Partner', 'Other', 'Custom'
));

-- 2. Add perspective-based relationship columns and primary partner flag
ALTER TABLE partner_connections
ADD COLUMN IF NOT EXISTS requester_relationship VARCHAR(50) DEFAULT 'Partner',
ADD COLUMN IF NOT EXISTS recipient_relationship VARCHAR(50) DEFAULT 'Partner',
ADD COLUMN IF NOT EXISTS requester_custom_label VARCHAR(100),
ADD COLUMN IF NOT EXISTS recipient_custom_label VARCHAR(100),
ADD COLUMN IF NOT EXISTS is_primary_partner BOOLEAN DEFAULT FALSE;

-- 3. Update existing records with fallback perspective
UPDATE partner_connections
SET requester_relationship = COALESCE(relationship, 'Partner')
WHERE requester_relationship IS NULL;

UPDATE partner_connections
SET recipient_relationship = COALESCE(relationship, 'Partner')
WHERE recipient_relationship IS NULL;

-- 4. Extend partner_permissions with owner_id and expanded permission types
ALTER TABLE partner_permissions
ADD COLUMN IF NOT EXISTS owner_id UUID REFERENCES users(id) ON DELETE CASCADE;

-- Backfill owner_id for existing permissions based on recipient_id
UPDATE partner_permissions pp
SET owner_id = pc.recipient_id
FROM partner_connections pc
WHERE pp.connection_id = pc.id AND pp.owner_id IS NULL;

ALTER TABLE partner_permissions
DROP CONSTRAINT IF EXISTS partner_permissions_permission_type_check;

ALTER TABLE partner_permissions
ADD CONSTRAINT partner_permissions_permission_type_check
CHECK (permission_type IN (
    'CYCLE_PHASE',
    'CYCLE_WINDOW',
    'OVULATION_WINDOW',
    'SYMPTOMS',
    'MOOD',
    'CARE_REQUESTS',
    'CARE_KIT',
    'WISHLIST',
    'REMINDERS',
    'SHOPPING',
    'DELIVERY_ADDRESS'
));

-- Update unique constraint to allow multi-directional permissions per connection
ALTER TABLE partner_permissions
DROP CONSTRAINT IF EXISTS unique_conn_permission;

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_conn_perm_owner 
ON partner_permissions(connection_id, permission_type, COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'::uuid));

-- 5. Sharing Audit Trail Table
CREATE TABLE IF NOT EXISTS sharing_audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID REFERENCES partner_connections(id) ON DELETE CASCADE,
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'REQUEST_SENT', 'ACCEPTED', 'DECLINED', 'REVOKED', 'BLOCKED',
        'PERMISSIONS_UPDATED', 'RELATIONSHIP_UPDATED', 'DATA_ACCESSED'
    )),
    target_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sharing_audit_conn ON sharing_audit_events(connection_id);
CREATE INDEX IF NOT EXISTS idx_sharing_audit_actor ON sharing_audit_events(actor_id);
CREATE INDEX IF NOT EXISTS idx_sharing_audit_created ON sharing_audit_events(created_at);

-- 6. Indexes for priority queries
CREATE INDEX IF NOT EXISTS idx_partner_conn_multi_status ON partner_connections(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_partner_conn_primary ON partner_connections(is_primary_partner);
