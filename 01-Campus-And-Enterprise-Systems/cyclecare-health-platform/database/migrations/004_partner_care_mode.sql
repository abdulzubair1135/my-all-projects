-- Migration 004: Partner Care Mode
-- Product Vision: Consent-based, privacy-first, permission-controlled, non-surveillance partner support system.
-- Tagline: "Support your partner • Prepare together • Send Care • Shared Care"

-- 1. Extend users table with cyclecare_id and usage_mode
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS cyclecare_id VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS usage_mode VARCHAR(50) DEFAULT 'TRACK_CYCLE' CHECK (usage_mode IN ('TRACK_CYCLE', 'SUPPORT_PARTNER', 'BOTH'));

-- 2. Partner Connections Table
CREATE TABLE IF NOT EXISTS partner_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'DECLINED', 'BLOCKED', 'REVOKED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accepted_at TIMESTAMP WITH TIME ZONE,
    declined_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_partner_pair UNIQUE(requester_id, recipient_id),
    CONSTRAINT cannot_connect_to_self CHECK (requester_id <> recipient_id)
);

CREATE INDEX IF NOT EXISTS idx_partner_conn_requester ON partner_connections(requester_id);
CREATE INDEX IF NOT EXISTS idx_partner_conn_recipient ON partner_connections(recipient_id);
CREATE INDEX IF NOT EXISTS idx_partner_conn_status ON partner_connections(status);

-- 3. Granular Partner Permissions Table (DEFAULT: ALL OFF)
CREATE TABLE IF NOT EXISTS partner_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID NOT NULL REFERENCES partner_connections(id) ON DELETE CASCADE,
    permission_type VARCHAR(50) NOT NULL CHECK (permission_type IN (
        'CYCLE_WINDOW',
        'CARE_KIT',
        'WISHLIST',
        'SYMPTOMS',
        'MOOD',
        'REMINDERS',
        'SHOPPING',
        'DELIVERY_ADDRESS'
    )),
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_conn_permission UNIQUE(connection_id, permission_type)
);

CREATE INDEX IF NOT EXISTS idx_partner_perm_conn ON partner_permissions(connection_id);

-- 4. Partner Invites Table
CREATE TABLE IF NOT EXISTS partner_invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invite_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partner_invites_token ON partner_invites(invite_token);

-- 5. Shared Delivery Addresses Table
CREATE TABLE IF NOT EXISTS shared_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connection_id UUID NOT NULL REFERENCES partner_connections(id) ON DELETE CASCADE,
    label VARCHAR(100) DEFAULT 'Home',
    address_line TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Extend orders table for Care Packages
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS buyer_id UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS recipient_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS care_package_message TEXT;

-- 7. RLS Security Policies for Partner Connections
ALTER TABLE partner_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_addresses ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    DROP POLICY IF EXISTS "Users can view their own connections" ON partner_connections;
    CREATE POLICY "Users can view their own connections" ON partner_connections
        FOR SELECT USING (auth.uid() = requester_id OR auth.uid() = recipient_id);

    DROP POLICY IF EXISTS "Users can view permissions of their active connection" ON partner_permissions;
    CREATE POLICY "Users can view permissions of their active connection" ON partner_permissions
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM partner_connections pc 
                WHERE pc.id = connection_id 
                AND (pc.requester_id = auth.uid() OR pc.recipient_id = auth.uid())
            )
        );

    DROP POLICY IF EXISTS "Connection data owner can update permissions" ON partner_permissions;
    CREATE POLICY "Connection data owner can update permissions" ON partner_permissions
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM partner_connections pc 
                WHERE pc.id = connection_id 
                AND pc.recipient_id = auth.uid()
            )
        );
END $$;
