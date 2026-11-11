import request from 'supertest';
import { createApp } from '../src/app';

describe('Phase 1: API Health Integration Test', () => {
  const app = createApp();

  it('GET /api/v1/health should return 200 and healthy status payload', async () => {
    const res = await request(app).get('/api/v1/health');

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data.status).toBe('healthy');
    expect(res.body.data.version).toBe('1.0.0');
  });

  it('Protected routes without Bearer token should return 401 Unauthorized', async () => {
    const res = await request(app).get('/api/v1/devices/my-devices');
    expect(res.status).toBe(401);
    expect(res.body.success).toBe(false);
  });
});
