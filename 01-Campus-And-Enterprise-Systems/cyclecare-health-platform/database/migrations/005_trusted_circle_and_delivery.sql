-- Migration 005: Trusted Circle, Demo Payments, Delivery Engine & Live Tracking
-- Product: CycleCare

-- 1. Extend partner_connections with relationship label
ALTER TABLE partner_connections
ADD COLUMN IF NOT EXISTS relationship VARCHAR(50) DEFAULT 'Partner' 
CHECK (relationship IN (
    'Mother', 'Father', 'Husband', 'Wife', 'Boyfriend', 'Girlfriend',
    'Best Friend', 'Sister', 'Brother', 'Family', 'Guardian', 'Partner', 'Other', 'Custom'
)),
ADD COLUMN IF NOT EXISTS custom_relationship_label VARCHAR(100);

-- 2. Extend orders table with lifecycle and tracking columns
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS order_number VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS order_status VARCHAR(50) DEFAULT 'PENDING'
CHECK (order_status IN ('PENDING', 'PAID', 'PROCESSING', 'PACKED', 'READY_FOR_DELIVERY', 'ASSIGNED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'ARRIVED', 'DELIVERED', 'CANCELLED', 'REFUNDED', 'FAILED')),
ADD COLUMN IF NOT EXISTS delivery_status VARCHAR(50) DEFAULT 'READY_FOR_DELIVERY',
ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS delivery_otp VARCHAR(10) DEFAULT '4821';

-- Ensure payments table supports DEMO provider
ALTER TABLE payments
ADD COLUMN IF NOT EXISTS provider VARCHAR(50) DEFAULT 'DEMO',
ADD COLUMN IF NOT EXISTS provider_transaction_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) DEFAULT 'DEMO_UPI';

-- 3. Delivery Agents Table
CREATE TABLE IF NOT EXISTS delivery_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) DEFAULT '+91 98765 43210',
    vehicle_type VARCHAR(50) DEFAULT 'Eco Electric Bike',
    vehicle_number VARCHAR(50) DEFAULT 'CC-DEL-01',
    status VARCHAR(50) DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'BUSY', 'OFFLINE')),
    is_active BOOLEAN DEFAULT TRUE,
    is_demo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delivery_agents_status ON delivery_agents(status);
CREATE INDEX IF NOT EXISTS idx_delivery_agents_demo ON delivery_agents(is_demo);

-- 4. Deliveries Table
CREATE TABLE IF NOT EXISTS deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES delivery_agents(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'READY_FOR_DELIVERY' 
    CHECK (status IN (
        'READY_FOR_DELIVERY', 'ASSIGNED', 'ACCEPTED', 'PICKED_UP',
        'OUT_FOR_DELIVERY', 'ARRIVED', 'DELIVERED', 'FAILED', 'CANCELLED'
    )),
    delivery_otp VARCHAR(10) DEFAULT '4821',
    pickup_time TIMESTAMP WITH TIME ZONE,
    assigned_at TIMESTAMP WITH TIME ZONE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    picked_up_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    arrived_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deliveries_order ON deliveries(order_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_agent ON deliveries(agent_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);

-- 5. Delivery Events Table
CREATE TABLE IF NOT EXISTS delivery_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    actor_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delivery_events_delivery ON delivery_events(delivery_id);

-- 6. Delivery Live Locations Table
CREATE TABLE IF NOT EXISTS delivery_live_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE UNIQUE,
    latitude DOUBLE PRECISION NOT NULL DEFAULT 28.6139,
    longitude DOUBLE PRECISION NOT NULL DEFAULT 77.2090,
    accuracy DOUBLE PRECISION DEFAULT 5.0,
    is_simulated BOOLEAN DEFAULT TRUE,
    progress_percent INTEGER DEFAULT 0,
    eta_minutes INTEGER DEFAULT 20,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delivery_live_loc ON delivery_live_locations(delivery_id);

-- 7. Inventory Movements Table
CREATE TABLE IF NOT EXISTS inventory_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('SALE', 'REFUND', 'CANCELLATION', 'ADMIN_ADJUSTMENT', 'RESTOCK')),
    reference_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_movements(product_id);

-- 8. Seed Demo Delivery Agent
DO $$
DECLARE
    v_demo_user_id UUID;
    v_agent_id UUID;
    v_demo_order_id UUID;
    v_first_product_id UUID;
    v_customer_user_id UUID;
BEGIN
    -- Ensure demo delivery agent user exists
    SELECT id INTO v_demo_user_id FROM users WHERE email = 'delivery.demo@cyclecare.app';
    IF v_demo_user_id IS NULL THEN
        INSERT INTO users (email, password_hash, cyclecare_id, usage_mode)
        VALUES ('delivery.demo@cyclecare.app', '$2b$10$wE0v1K6rJpWk401KkU0t..uG73w3zK55WzEw3P0vK.W82c5P6G84u', 'demodelivery', 'SUPPORT_PARTNER')
        RETURNING id INTO v_demo_user_id;

        INSERT INTO profiles (user_id, display_name)
        VALUES (v_demo_user_id, 'CycleCare Demo Courier')
        ON CONFLICT (user_id) DO NOTHING;
    END IF;

    -- Ensure delivery agent record exists
    SELECT id INTO v_agent_id FROM delivery_agents WHERE is_demo = TRUE;
    IF v_agent_id IS NULL THEN
        INSERT INTO delivery_agents (user_id, name, phone, vehicle_type, vehicle_number, status, is_active, is_demo)
        VALUES (v_demo_user_id, 'CycleCare Demo Courier', '+91 98765 43210', 'Eco Electric Bike', 'CC-DEMO-01', 'AVAILABLE', TRUE, TRUE)
        RETURNING id INTO v_agent_id;
    END IF;

    -- Ensure a customer exists for demo order
    SELECT id INTO v_customer_user_id FROM users WHERE email != 'delivery.demo@cyclecare.app' LIMIT 1;
    IF v_customer_user_id IS NULL THEN
        v_customer_user_id := v_demo_user_id;
    END IF;

    -- Ensure demo order #CC-DEMO-1001 exists
    SELECT id INTO v_demo_order_id FROM orders WHERE order_number = '#CC-DEMO-1001';
    IF v_demo_order_id IS NULL THEN
        INSERT INTO orders (
            order_number, user_id, buyer_id, recipient_user_id, subtotal, discount, delivery_fee, 
            total_amount, status, order_status, payment_status, delivery_status, 
            care_package_message, delivery_otp
        )
        VALUES (
            '#CC-DEMO-1001', v_customer_user_id, v_customer_user_id, v_customer_user_id, 368, 0, 0,
            368, 'PAID', 'READY_FOR_DELIVERY', 'SUCCESS', 'READY_FOR_DELIVERY',
            'Take care and stay hydrated! ❤️', '4821'
        )
        RETURNING id INTO v_demo_order_id;

        -- Create Delivery Record
        INSERT INTO deliveries (order_id, agent_id, status, delivery_otp)
        VALUES (v_demo_order_id, v_agent_id, 'READY_FOR_DELIVERY', '4821')
        ON CONFLICT DO NOTHING;
    END IF;

END $$;
