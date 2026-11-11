import request from 'supertest';
import app from '../src/app.js';
import pool from '../src/config/database.js';
import assert from 'assert';
import crypto from 'crypto';

describe('RentAny API Integration Tests', () => {
  let isDbConnected = false;
  let testUserToken = '';
  let otherUserToken = '';
  let testUserUuid = '';
  let otherUserUuid = '';
  let testListingId = null;
  let otherListingId = null;
  let adminToken = '';

  before(async () => {
    try {
      const conn = await pool.getConnection();
      isDbConnected = true;
      conn.release();
      console.log('  MySQL database is connected. Running database integration tests...');
    } catch (e) {
      console.log('  [Warning] MySQL is offline. Skipping database-dependent tests.');
    }
  });

  describe('1. Public Independent Endpoints', () => {
    it('GET / - API Health Check', async () => {
      const res = await request(app)
        .get('/')
        .expect(200);
      
      assert.strictEqual(res.body.success, true);
      assert.strictEqual(res.body.message, 'RentAny Production API Server is active and healthy.');
    });

    it('GET /api/any-fake-route - 404 handler', async () => {
      const res = await request(app)
        .get('/api/any-fake-route')
        .expect(404);
      
      assert.strictEqual(res.body.success, false);
    });
  });

  describe('2. Authentication APIs', () => {
    it('POST /api/v1/auth/register - Should register a new user', async function() {
      if (!isDbConnected) this.skip();

      const uniqueEmail = `testuser_${Date.now()}@test.com`;
      const uniquePhone = `+91${Math.floor(1000000000 + Math.random() * 9000000000)}`;
      
      const res = await request(app)
        .post('/api/v1/auth/register')
        .send({
          full_name: 'Test Renter',
          email: uniqueEmail,
          phone: uniquePhone,
          password: 'password123'
        })
        .expect(211); // 211 is what we set in controller
      
      assert.strictEqual(res.body.success, true);
      assert.ok(res.body.data.tokens.accessToken);
      testUserToken = `Bearer ${res.body.data.tokens.accessToken}`;
      testUserUuid = res.body.data.user.uuid;
    });

    it('POST /api/v1/auth/register - Should reject duplicate email', async function() {
      if (!isDbConnected) this.skip();

      const res = await request(app)
        .post('/api/v1/auth/register')
        .send({
          full_name: 'Amit Sharma Copy',
          email: 'amitsharma@gmail.com', // Already seeded
          phone: '+919999999999',
          password: 'password123'
        })
        .expect(409);
      
      assert.strictEqual(res.body.success, false);
    });

    it('POST /api/v1/auth/login - Should authenticate seeded user', async function() {
      if (!isDbConnected) this.skip();

      // Seeded user Amit Sharma
      const res = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'amitsharma@gmail.com',
          password: 'password123'
        })
        .expect(200);
      
      assert.strictEqual(res.body.success, true);
      otherUserToken = `Bearer ${res.body.data.tokens.accessToken}`;
      otherUserUuid = res.body.data.user.uuid;
    });

    it('POST /api/v1/auth/login - Should fail with incorrect password', async function() {
      if (!isDbConnected) this.skip();

      const res = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'amitsharma@gmail.com',
          password: 'wrongpassword'
        })
        .expect(401);
      
      assert.strictEqual(res.body.success, false);
    });
  });

  describe('3. Listings & Image Uploads', () => {
    it('POST /api/v1/listings - Create listing as authenticated owner', async function() {
      if (!isDbConnected) this.skip();

      const res = await request(app)
        .post('/api/v1/listings')
        .set('Authorization', testUserToken)
        .send({
          category_id: 2, // Electronics
          title: 'Mechanical Keyboard Renter',
          description: 'Custom hot-swappable mechanical keyboard for developers.',
          price_per_day: 150.00,
          refundable_deposit: 500.00,
          location_address: 'CG Road, Ahmedabad',
          city: 'Ahmedabad',
          state: 'Gujarat',
          country: 'India',
          postal_code: '380009',
          latitude: 23.0225,
          longitude: 72.5714
        })
        .expect(201);
      
      assert.strictEqual(res.body.success, true);
      testListingId = res.body.data.id;
    });

    it('PUT /api/v1/listings/:id - User B should not be able to edit User A listing (Ownership protection)', async function() {
      if (!isDbConnected) this.skip();

      const res = await request(app)
        .put(`/api/v1/listings/${testListingId}`)
        .set('Authorization', otherUserToken) // Logged in as Amit, testListing owned by Test Renter
        .send({
          title: 'Hacked Keyboard'
        })
        .expect(403);
      
      assert.strictEqual(res.body.success, false);
    });
  });

  describe('4. Bookings & Double-Booking Protection', () => {
    it('POST /api/bookings - Should create booking successfully via compatibility route', async function() {
      if (!isDbConnected) this.skip();

      // Renter: Rohan Patel (id: 1)
      // Listing: DSLR Camera (id: 1, owned by Amit)
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const afterTomorrow = new Date();
      afterTomorrow.setDate(afterTomorrow.getDate() + 3);

      const res = await request(app)
        .post('/api/bookings')
        .send({
          itemId: 1,
          startDate: tomorrow.toISOString().split('T')[0],
          endDate: afterTomorrow.toISOString().split('T')[0],
          deliveryType: 'Self Pickup'
        })
        .expect(200);
      
      assert.strictEqual(res.body.itemId, 1);
      assert.strictEqual(res.body.status, 'Upcoming');
    });

    it('POST /api/bookings - Should reject overlapping dates (Double-booking protection)', async function() {
      if (!isDbConnected) this.skip();

      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 2); // Overlaps with previous booking (day 1 to 3)
      const afterTomorrow = new Date();
      afterTomorrow.setDate(afterTomorrow.getDate() + 4);

      const res = await request(app)
        .post('/api/bookings')
        .send({
          itemId: 1,
          startDate: tomorrow.toISOString().split('T')[0],
          endDate: afterTomorrow.toISOString().split('T')[0],
          deliveryType: 'Self Pickup'
        })
        .expect(409); // Conflict
      
      assert.strictEqual(res.body.success, false);
      assert.strictEqual(res.body.message, 'The listing is already booked for the selected dates.');
    });
  });

  describe('5. Admin Authorization Rules', () => {
    it('GET /api/v1/admin/dashboard - Should deny access to regular user', async function() {
      if (!isDbConnected) this.skip();

      const res = await request(app)
        .get('/api/v1/admin/dashboard')
        .set('Authorization', testUserToken)
        .expect(403);
      
      assert.strictEqual(res.body.success, false);
    });

    it('GET /api/v1/admin/dashboard - Should permit access to administrative account', async function() {
      if (!isDbConnected) this.skip();

      // login as admin
      const loginRes = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'admin@rentany.com',
          password: 'password123'
        })
        .expect(200);

      adminToken = `Bearer ${loginRes.body.data.tokens.accessToken}`;

      const res = await request(app)
        .get('/api/v1/admin/dashboard')
        .set('Authorization', adminToken)
        .expect(200);
      
      assert.strictEqual(res.body.success, true);
      assert.ok(res.body.data.users);
    });
  });
});
