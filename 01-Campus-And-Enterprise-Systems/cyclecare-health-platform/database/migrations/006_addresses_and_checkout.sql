-- Migration 006: Addresses, Discreet Packaging, and Commerce Enhancements

-- 1. Ensure user_addresses columns
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS landmark VARCHAR(100);

-- 2. Ensure orders table has commerce & discreet delivery fields
ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_discreet_packaging BOOLEAN DEFAULT TRUE;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_notes TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_number VARCHAR(100);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_status VARCHAR(50) DEFAULT 'PROCESSING';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_status VARCHAR(50) DEFAULT 'ORDER_CONFIRMED';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'PENDING';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_otp VARCHAR(10);

-- 3. Snapshot product images in order items
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS image_url TEXT;
