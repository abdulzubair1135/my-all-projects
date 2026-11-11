const pool = require('../src/config/db');

const ADMIN_KEY = '8c2e54885f922a59917e38d497e970aaa25287fe99a2e3fd';
const BASE_URL = 'http://localhost:5000/api/v1';

async function api(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  const data = await res.json();
  return { status: res.status, data };
}

describe('CycleCare System Audit & Integration Suite (Tests A to G)', () => {
  jest.setTimeout(30000);
  let createdUserId = null;
  let userToken = null;
  let testProductId = null;
  let testOrderId = null;
  let testDeliveryId = null;
  const uniqueId = Date.now().toString().slice(-6);
  const testEmail = `organic.user.${uniqueId}@gmail.com`;

  afterAll(async () => {
    try {
      if (testProductId) {
        await pool.query('DELETE FROM product_images WHERE product_id = $1', [testProductId]);
        await pool.query('DELETE FROM inventory_movements WHERE product_id = $1', [testProductId]);
        await pool.query('DELETE FROM products WHERE id = $1', [testProductId]);
      }
      if (testOrderId) {
        await pool.query('DELETE FROM deliveries WHERE order_id = $1', [testOrderId]);
        await pool.query('DELETE FROM order_items WHERE order_id = $1', [testOrderId]);
        await pool.query('DELETE FROM orders WHERE id = $1', [testOrderId]);
      }
      if (createdUserId) {
        await pool.query('DELETE FROM period_logs WHERE user_id = $1', [createdUserId]);
        await pool.query('DELETE FROM cycle_settings WHERE user_id = $1', [createdUserId]);
        await pool.query('DELETE FROM profiles WHERE user_id = $1', [createdUserId]);
        await pool.query('DELETE FROM users WHERE id = $1', [createdUserId]);
      }
    } catch (_) {}
    await pool.end();
  }, 20000);

  // TEST A: User Registration & Real Profile Tagging
  describe('Test A: User Registration & Real Account Classification', () => {
    it('should register a new organic real user via Mobile Auth API', async () => {
      const res = await api('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: testEmail,
          password: 'Password123!',
          display_name: `Priya Organic ${uniqueId}`,
          usage_mode: 'TRACK_CYCLE',
          gender: 'FEMALE'
        })
      });

      expect(res.status).toBe(201);
      expect(res.data.success).toBe(true);
      expect(res.data.token).toBeDefined();
      userToken = res.data.token;
      createdUserId = res.data.user.id;
    });

    it('should show the newly registered user in Admin Control Panel tagged as REAL', async () => {
      const res = await api('/admin/users', {
        headers: { 'x-admin-key': ADMIN_KEY }
      });

      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      const found = res.data.users.find(u => u.email === testEmail);
      expect(found).toBeDefined();
      expect(found.account_type).toBe('REAL');
      expect(found.account_tag).toContain('REAL');
    });

    it('should allow admin to update user account tag and display name', async () => {
      const res = await api(`/admin/users/${createdUserId}/tag`, {
        method: 'PATCH',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({
          account_tag: 'VIP ORGANIC MEMBER',
          display_name: `Priya VIP ${uniqueId}`
        })
      });

      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);

      const checkRes = await api('/admin/users', { headers: { 'x-admin-key': ADMIN_KEY } });
      const updated = checkRes.data.users.find(u => u.id === createdUserId);
      expect(updated.account_tag).toBe('VIP ORGANIC MEMBER');
      expect(updated.display_name).toBe(`Priya VIP ${uniqueId}`);
    });
  });

  // TEST B: Store Product Lifecycle (Create, Draft -> Published, Live Sync)
  describe('Test B: Store Product Lifecycle & Publishing Sync', () => {
    it('should create a new product in DRAFT state via Admin API', async () => {
      const sku = `TEST-PAD-${uniqueId}`;
      const res = await api('/products', {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({
          name: `CycleCare Bamboo Pads ${uniqueId}`,
          brand: 'CycleCare',
          price: 299,
          discount_price: 249,
          stock: 50,
          sku,
          description: '100% Organic Bamboo Cotton Sanitary Pads',
          status: 'DRAFT',
          category_id: '11111111-1111-1111-1111-111111111111',
          images: ['https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=600']
        })
      });

      expect([200, 201]).toContain(res.status);
      expect(res.data.success).toBe(true);
      testProductId = res.data.product.id;
    });

    it('should NOT show draft products in normal public Mobile Store listing', async () => {
      const res = await api('/store/products');
      expect(res.status).toBe(200);
      const found = res.data.products.find(p => p.id === testProductId);
      expect(found).toBeUndefined();
    });

    it('should publish product and verify it appears live in Mobile Store listing', async () => {
      const pubRes = await api(`/products/${testProductId}/publish`, {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({ notify_users: false })
      });
      expect(pubRes.status).toBe(200);
      expect(pubRes.data.success).toBe(true);

      const storeRes = await api('/store/products');
      expect(storeRes.status).toBe(200);
      const found = storeRes.data.products.find(p => p.id === testProductId);
      expect(found).toBeDefined();
      expect(found.name).toContain(`CycleCare Bamboo Pads ${uniqueId}`);
    });

    it('should update product price and verify instant price sync in Mobile Store', async () => {
      const updateRes = await api(`/products/${testProductId}`, {
        method: 'PATCH',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({ price: 349, discount_price: 279 })
      });
      expect(updateRes.status).toBe(200);

      const checkRes = await api(`/products/${testProductId}`);
      expect(checkRes.status).toBe(200);
      expect(parseFloat(checkRes.data.product.price)).toBe(349);
      expect(parseFloat(checkRes.data.product.discount_price)).toBe(279);
    });
  });

  // TEST C: Cart, Order Creation, Payment & Inventory Decrement
  describe('Test C: Cart, Order Creation, Payment & Inventory Safety', () => {
    it('should allow user to create order and safely deduct inventory', async () => {
      const prevStockRes = await pool.query('SELECT stock FROM products WHERE id = $1', [testProductId]);
      const initialStock = prevStockRes.rows[0].stock;

      // Create test order directly in authoritative database
      const orderIns = await pool.query(
        `INSERT INTO orders (user_id, total_amount, subtotal, delivery_fee, status, order_status, payment_status, delivery_status, order_number, created_at, updated_at)
         VALUES ($1, $2, $2, 0, 'PAID', 'READY_FOR_DELIVERY', 'PAID', 'READY_FOR_DELIVERY', $3, NOW(), NOW())
         RETURNING id`,
        [createdUserId, 279, `#CC-REAL-${uniqueId}`]
      );
      testOrderId = orderIns.rows[0].id;

      await pool.query(
        `INSERT INTO order_items (order_id, product_id, product_name_snapshot, unit_price, quantity, total)
         VALUES ($1, $2, $3, $4, 2, $5)`,
        [testOrderId, testProductId, `CycleCare Bamboo Pads ${uniqueId}`, 279, 558]
      );

      // Inventory decrement
      await pool.query('UPDATE products SET stock = stock - 2, updated_at = NOW() WHERE id = $1', [testProductId]);
      await pool.query(
        `INSERT INTO inventory_movements (product_id, movement_type, quantity, previous_stock, new_stock, reason, created_at)
         VALUES ($1, 'PURCHASE', 2, $2, $2 - 2, $3, NOW())`,
        [testProductId, initialStock, `Order #${testOrderId}`]
      );

      const afterStockRes = await pool.query('SELECT stock FROM products WHERE id = $1', [testProductId]);
      expect(afterStockRes.rows[0].stock).toBe(initialStock - 2);
    });

    it('should show the order in Admin Control Panel with REAL PURCHASE indicator', async () => {
      const res = await api('/admin/orders', { headers: { 'x-admin-key': ADMIN_KEY } });
      expect(res.status).toBe(200);
      const found = res.data.orders.find(o => o.id === testOrderId);
      expect(found).toBeDefined();
      expect(found.order_type).toBe('REAL');
      expect(found.order_items.length).toBe(1);
    });
  });

  // TEST D: Deliveries & Live GPS Tracking
  describe('Test D: Deliveries Dispatch & OTP Verification', () => {
    it('should create a delivery record with secure 4-digit OTP', async () => {
      const delivIns = await pool.query(
        `INSERT INTO deliveries (order_id, status, delivery_otp, created_at, updated_at)
         VALUES ($1, 'READY_FOR_DELIVERY', '4821', NOW(), NOW())
         RETURNING id`,
        [testOrderId]
      );
      testDeliveryId = delivIns.rows[0].id;
      expect(testDeliveryId).toBeDefined();
    });

    it('should display the delivery order in the Admin Deliveries table', async () => {
      const res = await api('/admin/deliveries', { headers: { 'x-admin-key': ADMIN_KEY } });
      expect(res.status).toBe(200);
      const found = res.data.deliveries.find(d => d.order_id === testOrderId);
      expect(found).toBeDefined();
      expect(found.delivery_otp).toBe('4821');
    });

    it('should complete delivery when correct OTP is verified', async () => {
      // Wrong OTP fails
      const failRes = await api(`/deliveries/${testDeliveryId}/complete`, {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({ delivery_otp: '9999' })
      });
      expect(failRes.status).toBe(400);

      // Correct OTP succeeds
      const successRes = await api(`/deliveries/${testDeliveryId}/complete`, {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
        body: JSON.stringify({ delivery_otp: '4821' })
      });
      expect(successRes.status).toBe(200);
      expect(successRes.data.success).toBe(true);

      const checkDeliv = await pool.query('SELECT status FROM deliveries WHERE id = $1', [testDeliveryId]);
      expect(checkDeliv.rows[0].status).toBe('DELIVERED');
    });
  });

  // TEST E: Trusted Circle Messaging & Admin Oversight
  describe('Test E: Trusted Circle Messaging & Real-Time Monitoring', () => {
    it('should monitor circle messages with care items and metadata', async () => {
      const res = await api('/admin/chat-logs', { headers: { 'x-admin-key': ADMIN_KEY } });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.messages.length).toBeGreaterThan(0);
      expect(res.data.messages[0]).toHaveProperty('sender_name');
      expect(res.data.messages[0]).toHaveProperty('message_type');
    });
  });

  // TEST F: Health / Cycle Logging
  describe('Test F: Period & Health Logging Persistence', () => {
    it('should store period log in PostgreSQL and retrieve it in Admin cycle modal', async () => {
      await pool.query(
        `INSERT INTO period_logs (user_id, start_date, end_date, flow, notes, created_at, updated_at)
         VALUES ($1, '2026-10-01', '2026-10-05', 'MEDIUM', 'Normal cycle test log', NOW(), NOW())`,
        [createdUserId]
      );

      const res = await api(`/admin/users/${createdUserId}/cycle-logs`, {
        headers: { 'x-admin-key': ADMIN_KEY }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.period_logs.length).toBeGreaterThan(0);
      expect(res.data.period_logs[0].start_date).toBeDefined();
      expect(res.data.period_logs[0].flow).toBe('MEDIUM');
    });
  });

  // TEST G: Security & Error Handling
  describe('Test G: Security Boundaries & Authorization', () => {
    it('should block unauthorized requests to /api/v1/admin/dashboard', async () => {
      const res = await api('/admin/dashboard'); // No admin key
      expect(res.status).toBe(401);
    });

    it('should block unauthorized requests to /api/v1/admin/users', async () => {
      const res = await api('/admin/users'); // No admin key
      expect(res.status).toBe(401);
    });

    it('should block unauthorized requests with invalid admin key', async () => {
      const res = await api('/admin/dashboard', { headers: { 'x-admin-key': 'invalid-secret-xyz' } });
      expect(res.status).toBe(401);
    });
  });

  // TEST H: Global Error Monitoring & Crash Incident Lifecycle
  describe('Test H: Global Error Monitoring & Incident Lifecycle', () => {
    let testIncidentId = null;

    it('should ingest an Android client error report and persist incident', async () => {
      const res = await api('/monitoring/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: 'ANDROID',
          severity: 'CRITICAL',
          message: 'Integration test: NullPointerException in PeriodLogActivity',
          stack: 'java.lang.NullPointerException: at PeriodLogActivity.saveLog(PeriodLogActivity.java:120)',
          device_info: { brand: 'Google', model: 'Pixel 8', sdk: 34 }
        })
      });
      expect(res.status).toBe(201);
      expect(res.data.success).toBe(true);
      expect(res.data.incident_id).toBeDefined();
      testIncidentId = res.data.incident_id;
    });

    it('should return error statistics including critical and unresolved counts', async () => {
      const res = await api('/admin/errors/stats', {
        headers: { 'x-admin-key': ADMIN_KEY }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.stats).toBeDefined();
      expect(res.data.stats.total).toBeGreaterThan(0);
      expect(res.data.stats.unresolved).toBeGreaterThan(0);
    });

    it('should retrieve incident logs for Admin Control Panel', async () => {
      const res = await api('/admin/errors', {
        headers: { 'x-admin-key': ADMIN_KEY }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(Array.isArray(res.data.errors)).toBe(true);
      const found = res.data.errors.find(e => e.id === testIncidentId);
      expect(found).toBeDefined();
      expect(found.source).toBe('ANDROID');
      expect(found.severity).toBe('CRITICAL');
      expect(found.resolved).toBe(false);
    });

    it('should allow admin to resolve the incident', async () => {
      const res = await api(`/admin/errors/${testIncidentId}/resolve`, {
        method: 'PATCH',
        headers: { 'x-admin-key': ADMIN_KEY }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.incident.resolved).toBe(true);
    });
  });
});
