-- Migration 007: Circle Care Chat and In-Chat Care & Medical Item Sharing
-- Enables users to chat with partners, husbands, wives, parents, or trusted circle members,
-- and exchange/request care kits, pads, heating patches, relief items, and medical essentials.

CREATE TABLE IF NOT EXISTS circle_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID REFERENCES partner_connections(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL DEFAULT 'TEXT' CHECK (message_type IN ('TEXT', 'CARE_REQUEST', 'CARE_ITEM_SENT', 'EMERGENCY_SOS', 'CYCLE_UPDATE', 'PRESCRIPTION_MEDICINE')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circle_msg_conn ON circle_messages(connection_id);
CREATE INDEX IF NOT EXISTS idx_circle_msg_sender ON circle_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_circle_msg_receiver ON circle_messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_circle_msg_created ON circle_messages(created_at);

-- Add sample starter chat between demo customer and demo partner if not exists
DO $$
DECLARE
    v_cust_id UUID;
    v_partner_id UUID;
    v_conn_id UUID;
BEGIN
    SELECT id INTO v_cust_id FROM users WHERE email != 'delivery.demo@cyclecare.app' LIMIT 1;
    SELECT id INTO v_partner_id FROM users WHERE email = 'delivery.demo@cyclecare.app' LIMIT 1;

    IF v_cust_id IS NOT NULL AND v_partner_id IS NOT NULL THEN
        -- Check or insert connection
        SELECT id INTO v_conn_id FROM partner_connections 
        WHERE (requester_id = v_cust_id AND recipient_id = v_partner_id)
           OR (requester_id = v_partner_id AND recipient_id = v_cust_id);

        IF v_conn_id IS NULL THEN
            INSERT INTO partner_connections (requester_id, recipient_id, status, relationship)
            VALUES (v_cust_id, v_partner_id, 'ACCEPTED', 'Husband')
            RETURNING id INTO v_conn_id;
        END IF;

        -- Seed initial greeting & care request
        IF NOT EXISTS (SELECT 1 FROM circle_messages WHERE connection_id = v_conn_id) THEN
            INSERT INTO circle_messages (connection_id, sender_id, receiver_id, message_type, content, metadata)
            VALUES 
            (v_conn_id, v_partner_id, v_cust_id, 'TEXT', 'Hey! How are you feeling today? Let me know if you need anything.', '{}'::jsonb),
            (v_conn_id, v_cust_id, v_partner_id, 'CARE_REQUEST', 'Having some severe cramps today. Could you get me a heating patch and herbal tea?', 
             '{"item_name": "Instant Warmth Heat Patch", "item_price": 199, "item_category": "Comfort & Cramps", "item_image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80", "status": "REQUESTED"}'::jsonb),
            (v_conn_id, v_partner_id, v_cust_id, 'CARE_ITEM_SENT', 'Ordered the heat patch and dark chocolate for you! On the way ❤️', 
             '{"item_name": "Instant Warmth Heat Patch (Pack of 3)", "item_price": 199, "item_category": "Comfort", "item_image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80", "status": "ORDERED"}'::jsonb);
        END IF;
    END IF;
END $$;
