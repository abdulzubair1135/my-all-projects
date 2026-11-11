const request = require('supertest');

// Mock Supabase module to prevent network lookup timeouts during test runs
jest.mock('../src/config/supabase', () => ({
  from: jest.fn().mockImplementation((table) => ({
    select: jest.fn().mockReturnThis(),
    eq: jest.fn().mockReturnThis(),
    order: jest.fn().mockImplementation(() => {
      if (table === 'categories') {
        return Promise.resolve({
          data: [
            { id: '11111111-1111-1111-1111-111111111111', name: 'Period Care', is_active: true }
          ],
          error: null
        });
      }
      if (table === 'wellness_articles') {
        return Promise.resolve({
          data: [
            { id: 'w1', title: 'Understanding Your Menstrual Cycle Phases', status: 'PUBLISHED' }
          ],
          error: null
        });
      }
      return Promise.resolve({ data: [], error: null });
    })
  }))
}));

const app = require('../src/app');

describe('CycleCare API Health & Public Routes', () => {
  it('GET /api/v1/health should return ok and service name', async () => {
    const res = await request(app).get('/api/v1/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toEqual({
      status: 'ok',
      service: 'CycleCare API',
      version: '1.0.0'
    });
  });

  it('GET / should return 200 and server metadata', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('name', 'CycleCare API Server');
    expect(res.body).toHaveProperty('status', 'ONLINE');
  });

  it('GET /api/v1/store/categories should return active store categories', async () => {
    const res = await request(app).get('/api/v1/store/categories');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('success', true);
    expect(res.body.categories.length).toBeGreaterThan(0);
  });

  it('GET /api/v1/wellness/articles should return published wellness articles', async () => {
    const res = await request(app).get('/api/v1/wellness/articles');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('success', true);
    expect(res.body.articles.length).toBeGreaterThan(0);
  });
});

describe('CycleCare Security & Input Validation', () => {
  it('POST /api/v1/auth/register should reject empty payload with 400', async () => {
    const res = await request(app).post('/api/v1/auth/register').send({});
    expect(res.statusCode).toEqual(400);
    expect(res.body).toHaveProperty('success', false);
  });

  it('POST /api/v1/auth/login should reject empty payload with 400', async () => {
    const res = await request(app).post('/api/v1/auth/login').send({});
    expect(res.statusCode).toEqual(400);
    expect(res.body).toHaveProperty('success', false);
  });

  it('GET /api/v1/cycle should reject unauthorized requests without JWT token', async () => {
    const res = await request(app).get('/api/v1/cycle');
    expect(res.statusCode).toEqual(401);
    expect(res.body).toHaveProperty('code', 'UNAUTHORIZED');
  });

  it('GET /api/v1/admin/dashboard should reject non-admin requests without authorization', async () => {
    const res = await request(app).get('/api/v1/admin/dashboard');
    expect(res.statusCode).toEqual(401);
  });
});

describe('Cycle Estimation Logic & Medical Disclaimer', () => {
  const { calculateCycleMetrics } = require('../src/services/cycleService');

  it('should provide estimate and explicit medical disclaimer', () => {
    const metrics = calculateCycleMetrics([
      { start_date: '2026-09-01', end_date: '2026-09-06' },
      { start_date: '2026-08-03', end_date: '2026-08-08' }
    ], { average_cycle_length: 29 });

    expect(metrics).toHaveProperty('disclaimer');
    expect(metrics.disclaimer).toContain('Cycle predictions are estimates');
    expect(metrics.disclaimer).toContain('never be treated as medical certainty');
    expect(metrics.hasSufficientData).toBe(true);
  });
});
