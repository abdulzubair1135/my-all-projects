-- CycleCare Supabase PostgreSQL Database Migration
-- Migration 002: Row Level Security (RLS) Policies and Initial Seed Data

-- ENABLE ROW LEVEL SECURITY
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cycle_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE period_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE care_kits ENABLE ROW LEVEL SECURITY;
ALTER TABLE care_kit_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_product_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;
-- RLS POLICIES FOR USER DATA ISOLATION (Only access own records)
DO $$
BEGIN
    -- Users table
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view and update own profile' AND tablename = 'users') THEN
        CREATE POLICY "Users can view and update own profile" ON users FOR ALL USING (auth.uid() = id);
    END IF;

    -- Profiles
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own profile' AND tablename = 'profiles') THEN
        CREATE POLICY "Users can access own profile" ON profiles FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Cycle Settings
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own cycle settings' AND tablename = 'cycle_settings') THEN
        CREATE POLICY "Users can access own cycle settings" ON cycle_settings FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Period Logs
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own period logs' AND tablename = 'period_logs') THEN
        CREATE POLICY "Users can access own period logs" ON period_logs FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Symptom Logs
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own symptom logs' AND tablename = 'symptom_logs') THEN
        CREATE POLICY "Users can access own symptom logs" ON symptom_logs FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Mood Logs
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own mood logs' AND tablename = 'mood_logs') THEN
        CREATE POLICY "Users can access own mood logs" ON mood_logs FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Reminders
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own reminders' AND tablename = 'reminders') THEN
        CREATE POLICY "Users can access own reminders" ON reminders FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Cart & Cart Items
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own cart' AND tablename = 'cart') THEN
        CREATE POLICY "Users can access own cart" ON cart FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Wishlist
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own wishlist' AND tablename = 'wishlist') THEN
        CREATE POLICY "Users can access own wishlist" ON wishlist FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Addresses
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own addresses' AND tablename = 'addresses') THEN
        CREATE POLICY "Users can access own addresses" ON addresses FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Orders
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own orders' AND tablename = 'orders') THEN
        CREATE POLICY "Users can access own orders" ON orders FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Care Kits
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own care kits' AND tablename = 'care_kits') THEN
        CREATE POLICY "Users can access own care kits" ON care_kits FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- AI Conversations
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can access own AI conversations' AND tablename = 'ai_conversations') THEN
        CREATE POLICY "Users can access own AI conversations" ON ai_conversations FOR ALL USING (auth.uid() = user_id);
    END IF;
END $$;
-- SEED DATA: Default Symptoms
INSERT INTO symptoms (name, category) VALUES
('Cramps', 'Physical'),
('Headache', 'Physical'),
('Back pain', 'Physical'),
('Bloating', 'Physical'),
('Acne', 'Skin'),
('Fatigue', 'Physical'),
('Nausea', 'Digestive'),
('Appetite changes', 'Digestive'),
('Sleep changes', 'Physical'),
('Breast Tenderness', 'Physical')
ON CONFLICT (name) DO NOTHING;

-- SEED DATA: Default Moods
INSERT INTO moods (name, icon_name) VALUES
('Happy', 'ic_mood_happy'),
('Good', 'ic_mood_good'),
('Neutral', 'ic_mood_neutral'),
('Sad', 'ic_mood_sad'),
('Irritated', 'ic_mood_irritated'),
('Stressed', 'ic_mood_stressed'),
('Tired', 'ic_mood_tired')
ON CONFLICT (name) DO NOTHING;

-- SEED DATA: Categories
INSERT INTO categories (id, name, description, is_active) VALUES
('11111111-1111-1111-1111-111111111111', 'Period Care', 'Pads, pantyliners, tampons, and period underwear for comfort & protection.', true),
('22222222-2222-2222-2222-222222222222', 'Comfort & Relief', 'Heating pads, hot/cold packs, soothing patches and body care.', true),
('33333333-3333-3333-3333-333333333333', 'Personal Care & Hygiene', 'Intimate wipes, organic cleansers, and personal care essentials.', true),
('44444444-4444-4444-4444-444444444444', 'Snacks & Beverages', 'Comfort dark chocolate, herbal teas, and soothing drinks.', true)
ON CONFLICT DO NOTHING;

-- SEED DATA: Sample Products
INSERT INTO products (id, category_id, name, description, price, discount_price, stock, sku, is_active) VALUES
('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'CycleCare Organic Cotton Pads (Night)', 'Soft, ultra-absorbent organic cotton pads with heavy flow leak guards. Pack of 10.', 149.00, 129.00, 100, 'PAD-NIGHT-01', true),
('a2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'CycleCare Ultra-Thin Daily Pantyliners', 'Breathable daily pantyliners for fresh comfort. Pack of 20.', 99.00, 89.00, 150, 'LINER-THIN-01', true),
('b1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Instant Warmth Heat Patch (Pack of 3)', 'Air-activated heating patches that soothe menstrual cramps for up to 8 hours.', 199.00, 169.00, 80, 'HEAT-PATCH-03', true),
('b2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'Soothing Electric Heating Water Bag', 'Rechargeable electric hot water bag for abdominal and back cramp relief.', 399.00, 349.00, 40, 'E-HOTBAG-01', true),
('c1111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'Gentle pH-Balanced Intimate Wipes', 'Biodegradable intimate hygiene wipes infused with aloe vera and chamomile. Pack of 15.', 85.00, 75.00, 120, 'WIPES-ALOE-15', true),
('d1111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', 'CycleCare Period Comfort Dark Chocolate (70%)', 'Rich Belgian dark chocolate infused with magnesium and berry flavor.', 120.00, 99.00, 200, 'CHOC-DARK-70', true),
('d2222222-2222-2222-2222-222222222222', '44444444-4444-4444-4444-444444444444', 'Chamomile & Ginger Soothing Herbal Tea', 'Caffeine-free herbal infusion to relieve bloating and relax muscles. 15 Tea Bags.', 180.00, 150.00, 90, 'TEA-HERBAL-15', true)
ON CONFLICT DO NOTHING;

-- SEED DATA: Wellness Categories
INSERT INTO wellness_categories (id, name) VALUES
('f1111111-1111-1111-1111-111111111111', 'Cycle Basics'),
('f2222222-2222-2222-2222-222222222222', 'Period Hygiene'),
('f3333333-3333-3333-3333-333333333333', 'PMS & Cramp Relief'),
('f4444444-4444-4444-4444-444444444444', 'Myth vs Fact')
ON CONFLICT DO NOTHING;

-- SEED DATA: Wellness Articles
INSERT INTO wellness_articles (title, category_id, content, status) VALUES
('Understanding Your Menstrual Cycle Phases', 'f1111111-1111-1111-1111-111111111111', 'The menstrual cycle is divided into four main phases: the menstrual phase, follicular phase, ovulation, and luteal phase. Understanding each phase helps you tune into body changes, energy levels, and mood shifts.', 'PUBLISHED'),
('Best Practices for Period Hygiene', 'f2222222-2222-2222-2222-222222222222', 'Change sanitary products regularly (every 4-6 hours for pads, 4-8 hours for tampons). Wash gently with water and mild pH-balanced cleanser. Always wash from front to back to prevent bacterial transfer.', 'PUBLISHED'),
('Natural Ways to Relieve Menstrual Cramps', 'f3333333-3333-3333-3333-333333333333', 'Heat therapy, gentle stretching, stay hydrated, drink chamomile tea, and ensure adequate magnesium intake through foods like dark chocolate, nuts, and leafy greens.', 'PUBLISHED'),
('Myth vs Fact: Can You Exercise During Your Period?', 'f4444444-4444-4444-4444-444444444444', 'MYTH: You should avoid all exercise during your period.\nFACT: Light to moderate exercise such as walking, yoga, and swimming can actually reduce cramps, boost mood, and improve circulation!', 'PUBLISHED')
ON CONFLICT DO NOTHING;
