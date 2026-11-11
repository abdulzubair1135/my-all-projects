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

describe('CycleCare Relationship-Based Partner & Family Sharing Test Suite', () => {
  jest.setTimeout(45000);

  const timestamp = Date.now().toString().slice(-6);
  const users = {
    woman: { email: `woman.${timestamp}@example.com`, pass: 'TestPass123!', name: `Ananya ${timestamp}`, token: null, id: null },
    husband: { email: `husband.${timestamp}@example.com`, pass: 'TestPass123!', name: `Rahul ${timestamp}`, token: null, id: null },
    daughter1: { email: `daughter1.${timestamp}@example.com`, pass: 'TestPass123!', name: `Diya ${timestamp}`, token: null, id: null },
    daughter2: { email: `daughter2.${timestamp}@example.com`, pass: 'TestPass123!', name: `Riya ${timestamp}`, token: null, id: null },
    friend: { email: `friend.${timestamp}@example.com`, pass: 'TestPass123!', name: `Kavita ${timestamp}`, token: null, id: null },
    stranger: { email: `stranger.${timestamp}@example.com`, pass: 'TestPass123!', name: `Stranger ${timestamp}`, token: null, id: null },
  };

  let husbandConnId = null;
  let daughter1ConnId = null;
  let daughter2ConnId = null;
  let friendConnId = null;

  beforeAll(async () => {
    // Register all test users
    for (const key of Object.keys(users)) {
      const u = users[key];
      const reg = await api('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: u.email,
          password: u.pass,
          display_name: u.name,
          usage_mode: 'TRACK_CYCLE'
        })
      });
      if (reg.status === 201 || reg.status === 200) {
        u.token = reg.data.token;
        u.id = reg.data.user.id;
      } else {
        // Login fallback if user already exists
        const login = await api('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email: u.email, password: u.pass })
        });
        u.token = login.data.token;
        u.id = login.data.user.id;
      }
    }

    // Insert active cycle log for woman so cycle calculations can be tested
    await pool.query(
      `INSERT INTO period_logs (user_id, start_date, end_date, flow)
       VALUES ($1, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '6 days', 'MEDIUM')
       ON CONFLICT DO NOTHING`,
      [users.woman.id]
    );
  });

  afterAll(async () => {
    try {
      const allIds = Object.values(users).map(u => u.id).filter(Boolean);
      if (allIds.length > 0) {
        await pool.query('DELETE FROM sharing_audit_events WHERE actor_id = ANY($1) OR target_user_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM partner_permissions WHERE granted_by = ANY($1) OR grantee_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM partner_connections WHERE requester_id = ANY($1) OR recipient_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM period_logs WHERE user_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM cycle_settings WHERE user_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM profiles WHERE user_id = ANY($1)', [allIds]);
        await pool.query('DELETE FROM users WHERE id = ANY($1)', [allIds]);
      }
    } catch (_) {}
    await pool.end();
  }, 25000);

  // 1. Connection Requests with Perspective-Aware Labels
  describe('1. Perspective-Aware Relationship Connection Requests', () => {
    it('should send connection request from Husband to Woman tagged as Wife / Husband', async () => {
      const res = await api('/partner/request', {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.husband.token}` },
        body: JSON.stringify({
          recipient_email: users.woman.email,
          relationship: 'Wife',
          requester_relationship: 'Husband',
          recipient_relationship: 'Wife'
        })
      });
      expect(res.status).toBe(201);
      expect(res.data.success).toBe(true);
      expect(res.data.connection).toBeDefined();
      husbandConnId = res.data.connection.id;
    });

    it('should send connection request from Woman to Daughter 1', async () => {
      const res = await api('/partner/request', {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.woman.token}` },
        body: JSON.stringify({
          recipient_email: users.daughter1.email,
          relationship: 'Daughter',
          requester_relationship: 'Mother',
          recipient_relationship: 'Daughter'
        })
      });
      expect(res.status).toBe(201);
      daughter1ConnId = res.data.connection.id;
    });

    it('should send connection request from Woman to Daughter 2 (Multi-family member)', async () => {
      const res = await api('/partner/request', {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.woman.token}` },
        body: JSON.stringify({
          recipient_email: users.daughter2.email,
          relationship: 'Daughter',
          requester_relationship: 'Mother',
          recipient_relationship: 'Daughter'
        })
      });
      expect(res.status).toBe(201);
      daughter2ConnId = res.data.connection.id;
    });

    it('should send connection request from Woman to Friend', async () => {
      const res = await api('/partner/request', {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.woman.token}` },
        body: JSON.stringify({
          recipient_email: users.friend.email,
          relationship: 'Best Friend',
          requester_relationship: 'Best Friend',
          recipient_relationship: 'Best Friend'
        })
      });
      expect(res.status).toBe(201);
      friendConnId = res.data.connection.id;
    });
  });

  // 2. Acceptance and Opt-In Permission Defaults
  describe('2. Acceptance and Default Permission Verification', () => {
    it('Woman accepts Husband connection request', async () => {
      const res = await api(`/partner/requests/${husbandConnId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.woman.token}` },
        body: JSON.stringify({ reciprocal_relationship: 'Husband' })
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.connection.status).toBe('ACCEPTED');
    });

    it('Daughter 1 accepts Woman connection request', async () => {
      const res = await api(`/partner/requests/${daughter1ConnId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.daughter1.token}` },
        body: JSON.stringify({ reciprocal_relationship: 'Mother' })
      });
      expect(res.status).toBe(200);
      expect(res.data.connection.status).toBe('ACCEPTED');
    });

    it('Daughter 2 accepts Woman connection request', async () => {
      const res = await api(`/partner/requests/${daughter2ConnId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.daughter2.token}` },
        body: JSON.stringify({ reciprocal_relationship: 'Mother' })
      });
      expect(res.status).toBe(200);
    });

    it('Friend accepts Woman connection request', async () => {
      const res = await api(`/partner/requests/${friendConnId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${users.friend.token}` },
        body: JSON.stringify({ reciprocal_relationship: 'Best Friend' })
      });
      expect(res.status).toBe(200);
    });

    it('Default permissions must all be false (Opt-in only consent)', async () => {
      const res = await api(`/partner/${husbandConnId}/permissions`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.woman.token}` }
      });
      expect(res.status).toBe(200);
      expect(res.data.permissions).toBeDefined();
      // All permission categories must default to false
      Object.keys(res.data.permissions).forEach(key => {
        expect(res.data.permissions[key]).toBe(false);
      });
    });
  });

  // 3. Priority Ordering & Multi-Member Family List
  describe('3. Priority-Ranked List Resolution & Multi-Family Members', () => {
    it('Woman sees primary partner (Husband) and ALL family members without dropping any', async () => {
      const res = await api('/partner/connections', {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.woman.token}` }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);

      // Primary partner must be Husband (Priority 1)
      expect(res.data.primary_partner).toBeDefined();
      expect(res.data.primary_partner.priority_rank).toBe(1);
      expect(res.data.primary_partner.resolved_relationship.toLowerCase()).toContain('husband');

      // Both daughters and friend must be present in all_active list
      expect(res.data.all_active.length).toBe(4);

      // Priority ordering verification: Rank 1 (Husband) comes before Rank 3 (Daughters) before Rank 4 (Friend)
      const ranks = res.data.all_active.map(c => c.priority_rank);
      expect(ranks[0]).toBe(1); // Husband
      expect(ranks[1]).toBe(3); // Daughter 1 or 2
      expect(ranks[2]).toBe(3); // Daughter 1 or 2
      expect(ranks[3]).toBe(4); // Best Friend
    });

    it('Safe fallback prevents null display_name', async () => {
      const res = await api('/partner/connections', {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.woman.token}` }
      });
      res.data.all_active.forEach(member => {
        expect(member.partner_profile.display_name).toBeTruthy();
        expect(member.partner_profile.display_name).not.toBe('null');
        expect(typeof member.partner_profile.display_name).toBe('string');
      });
    });
  });

  // 4. Permission Gating & Privacy Enforcement
  describe('4. Granular Permission Gating & Non-Surveillance Fallbacks', () => {
    it('Husband queries member status before permissions are granted -> NOT_SHARED', async () => {
      const res = await api(`/partner/${husbandConnId}/member-status`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.husband.token}` }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      // Privacy check: sensitive cycle and symptoms must indicate NOT_SHARED
      expect(res.data.status.cycle_phase.permitted).toBe(false);
      expect(res.data.status.cycle_phase.status).toBe('NOT_SHARED');
      expect(res.data.status.symptoms.permitted).toBe(false);
      expect(res.data.status.symptoms.items).toEqual([]);
    });

    it('Woman grants CYCLE_PHASE and REMINDERS permissions to Husband', async () => {
      const res = await api(`/partner/${husbandConnId}/permissions`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${users.woman.token}` },
        body: JSON.stringify({
          permissions: {
            CYCLE_PHASE: true,
            REMINDERS: true,
            SYMPTOMS: false
          }
        })
      });
      expect(res.status).toBe(200);
      expect(res.data.permissions.CYCLE_PHASE).toBe(true);
      expect(res.data.permissions.REMINDERS).toBe(true);
      expect(res.data.permissions.SYMPTOMS).toBe(false);
    });

    it('Husband queries member status after CYCLE_PHASE is granted -> sees phase info & non-medical disclaimer', async () => {
      const res = await api(`/partner/${husbandConnId}/member-status`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.husband.token}` }
      });
      expect(res.status).toBe(200);
      expect(res.data.status.cycle_phase.permitted).toBe(true);
      expect(res.data.status.cycle_phase.phase).toBeTruthy();
      expect(res.data.status.cycle_phase.medical_disclaimer).toBeDefined();

      // Symptoms still unpermitted
      expect(res.data.status.symptoms.permitted).toBe(false);
      expect(res.data.status.symptoms.status).toBe('NOT_SHARED');
    });
  });

  // 5. Anti-Tampering & Security Boundaries
  describe('5. Access Control & Tampering Prevention', () => {
    it('Stranger cannot access or modify permissions for Woman-Husband connection (403/404)', async () => {
      const res = await api(`/partner/${husbandConnId}/permissions`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${users.stranger.token}` },
        body: JSON.stringify({ permissions: { CYCLE_PHASE: true } })
      });
      expect(res.status).toBe(403);
    });

    it('Stranger cannot query member status for Woman-Husband connection (403)', async () => {
      const res = await api(`/partner/${husbandConnId}/member-status`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.stranger.token}` }
      });
      expect(res.status).toBe(403);
    });
  });

  // 6. Immediate Revocation & Access Blocking
  describe('6. Revocation Enforcement', () => {
    it('Woman revokes Husband connection', async () => {
      const res = await api(`/partner/${husbandConnId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${users.woman.token}` }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
    });

    it('Husband querying revoked connection immediately receives 403 Forbidden', async () => {
      const res = await api(`/partner/${husbandConnId}/member-status`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${users.husband.token}` }
      });
      expect(res.status).toBe(403);
      expect(res.data.error).toContain('Connection is not active');
    });
  });

  // 7. Admin Control Panel Operational Diagnostics
  describe('7. Admin Control Panel Operational Diagnostics', () => {
    it('Admin queries /admin/sharing/diagnostics and receives aggregated operational stats', async () => {
      const res = await api('/admin/sharing/diagnostics', {
        method: 'GET',
        headers: { 'x-admin-key': ADMIN_KEY }
      });
      expect(res.status).toBe(200);
      expect(res.data.success).toBe(true);
      expect(res.data.diagnostics).toBeDefined();
      expect(typeof res.data.diagnostics.totalConnections).toBe('number');
      expect(res.data.diagnostics.statusBreakdown).toBeDefined();
      expect(res.data.diagnostics.relationshipDistribution).toBeDefined();
      expect(res.data.diagnostics.recentAuditEvents).toBeDefined();

      // Zero private health logs or cycle information in diagnostics payload
      const payloadStr = JSON.stringify(res.data.diagnostics);
      expect(payloadStr).not.toContain('flow_intensity');
      expect(payloadStr).not.toContain('period_logs');
    });
  });
});
