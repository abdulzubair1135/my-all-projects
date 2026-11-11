const dns = require('dns');
try { dns.setServers(['8.8.8.8', '1.1.1.1']); } catch (_) {}
const request = require('supertest');
const app = require('../src/app');
const pool = require('../src/config/db');
const {
  CANONICAL_RELATIONSHIPS,
  normalizeRelationshipTag,
  validateCompatibility,
  getAmbiguityOptions,
  determineReciprocal
} = require('../src/services/relationshipMappingService');

describe('CycleCare Automatic Reciprocal Relationship Tagging System', () => {
  jest.setTimeout(45000);

  const timestamp = Date.now().toString().slice(-6);
  const users = {
    father: { email: `father.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Papa ${timestamp}`, gender: 'MALE', usage_mode: 'SUPPORT_PARTNER', token: null, id: null },
    mother: { email: `mother.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Maa ${timestamp}`, gender: 'FEMALE', usage_mode: 'TRACK_CYCLE', token: null, id: null },
    daughter: { email: `daughter.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Diya ${timestamp}`, gender: 'FEMALE', usage_mode: 'TRACK_CYCLE', token: null, id: null },
    son: { email: `son.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Aarav ${timestamp}`, gender: 'MALE', usage_mode: 'SUPPORT_PARTNER', token: null, id: null },
    brother: { email: `brother.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Rohit ${timestamp}`, gender: 'MALE', usage_mode: 'SUPPORT_PARTNER', token: null, id: null },
    sister: { email: `sister.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Pooja ${timestamp}`, gender: 'FEMALE', usage_mode: 'TRACK_CYCLE', token: null, id: null },
    husband: { email: `husband.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Rahul ${timestamp}`, gender: 'MALE', usage_mode: 'SUPPORT_PARTNER', token: null, id: null },
    wife: { email: `wife.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Ananya ${timestamp}`, gender: 'FEMALE', usage_mode: 'TRACK_CYCLE', token: null, id: null },
    stranger: { email: `stranger.${timestamp}@test.cyclecare.app`, pass: 'TestPass123!', name: `Stranger ${timestamp}`, gender: 'FEMALE', usage_mode: 'TRACK_CYCLE', token: null, id: null }
  };

  beforeAll(async () => {
    // 1. Register test users via standard auth endpoint
    for (const key of Object.keys(users)) {
      const u = users[key];
      const regRes = await request(app)
        .post('/api/v1/auth/register')
        .send({
          email: u.email,
          password: u.pass,
          display_name: u.name,
          usage_mode: u.usage_mode
        });

      if (regRes.status === 201 || regRes.status === 200) {
        u.token = regRes.body.token;
        u.id = regRes.body.user.id;
      } else {
        const loginRes = await request(app)
          .post('/api/v1/auth/login')
          .send({ email: u.email, password: u.pass });
        u.token = loginRes.body.token;
        u.id = loginRes.body.user.id;
      }

      // Ensure explicit gender and usage_mode in database
      await pool.query('UPDATE users SET gender = $1, usage_mode = $2 WHERE id = $3', [u.gender, u.usage_mode, u.id]);
      await pool.query('UPDATE profiles SET gender = $1 WHERE user_id = $2', [u.gender, u.id]);
    }
  });

  afterAll(async () => {
    // Cleanup
    const userIds = Object.values(users).map(u => u.id).filter(Boolean);
    if (userIds.length > 0) {
      await pool.query('DELETE FROM sharing_audit_events WHERE actor_id = ANY($1)', [userIds]);
      await pool.query('DELETE FROM partner_connections WHERE requester_id = ANY($1) OR recipient_id = ANY($1)', [userIds]);
      await pool.query('DELETE FROM profiles WHERE user_id = ANY($1)', [userIds]);
      await pool.query('DELETE FROM users WHERE id = ANY($1)', [userIds]);
    }
  });

  // ==============================================================
  // 1. Centralized Relationship Service Logic & Normalization
  // ==============================================================
  describe('1. Centralized Relationship Service Logic & Normalization', () => {
    test('Tag normalization should clean emojis, whitespace, and regional synonyms', () => {
      expect(normalizeRelationshipTag('Husband 💍')).toBe('Husband');
      expect(normalizeRelationshipTag('  Wife 👩  ')).toBe('Wife');
      expect(normalizeRelationshipTag('Dad')).toBe('Father');
      expect(normalizeRelationshipTag('Papa')).toBe('Father');
      expect(normalizeRelationshipTag('Mom')).toBe('Mother');
      expect(normalizeRelationshipTag('Mummy')).toBe('Mother');
      expect(normalizeRelationshipTag('Beti')).toBe('Daughter');
      expect(normalizeRelationshipTag('Beta')).toBe('Son');
      expect(normalizeRelationshipTag('Bro')).toBe('Brother');
      expect(normalizeRelationshipTag('Bhai')).toBe('Brother');
      expect(normalizeRelationshipTag('Sis')).toBe('Sister');
      expect(normalizeRelationshipTag('Didi')).toBe('Sister');
      expect(normalizeRelationshipTag('Best Friend 🤝')).toBe('Best Friend');
      expect(normalizeRelationshipTag('Friend ⭐')).toBe('Best Friend');
      expect(normalizeRelationshipTag('Spouse')).toBe('Partner');
    });

    test('Compatibility validation should correctly approve valid and reject invalid pairs', () => {
      expect(validateCompatibility('Husband', 'Wife').valid).toBe(true);
      expect(validateCompatibility('Father', 'Daughter').valid).toBe(true);
      expect(validateCompatibility('Father', 'Son').valid).toBe(true);
      expect(validateCompatibility('Father', 'Husband').valid).toBe(false);
      expect(validateCompatibility('Mother', 'Wife').valid).toBe(false);
      expect(validateCompatibility('Brother', 'Sister').valid).toBe(true);
      expect(validateCompatibility('Brother', 'Brother').valid).toBe(true);
      expect(validateCompatibility('Sister', 'Sister').valid).toBe(true);
    });

    test('Ambiguity detection identifies pairings needing clarification when gender is absent', () => {
      expect(getAmbiguityOptions('Father')).toEqual(['Daughter', 'Son']);
      expect(getAmbiguityOptions('Mother')).toEqual(['Daughter', 'Son']);
      expect(getAmbiguityOptions('Daughter')).toEqual(['Mother', 'Father']);
      expect(getAmbiguityOptions('Son')).toEqual(['Mother', 'Father']);
      expect(getAmbiguityOptions('Brother')).toEqual(['Sister', 'Brother']);
      expect(getAmbiguityOptions('Sister')).toEqual(['Sister', 'Brother']);
      expect(getAmbiguityOptions('Best Friend')).toEqual([]);
    });

    test('Strict ambiguity mode throws error when actor gender cannot be inferred', () => {
      expect(() => {
        determineReciprocal({
          assignedTag: 'Father',
          actorGender: null,
          actorUsageMode: null,
          strictAmbiguity: true
        });
      }).toThrow(/Reciprocal relationship for Father is ambiguous/);
    });
  });

  // ==============================================================
  // 2. Bidirectional Relationship Pairing Matrix
  // ==============================================================
  describe('2. Bidirectional Reciprocal Determination Matrix', () => {
    test('A (Female) tags B as Husband -> B sees A as Wife', () => {
      const res = determineReciprocal({ assignedTag: 'Husband', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Husband');
      expect(res.reciprocal).toBe('Wife');
    });

    test('A (Male) tags B as Wife -> B sees A as Husband', () => {
      const res = determineReciprocal({ assignedTag: 'Wife', actorGender: 'MALE' });
      expect(res.assigned).toBe('Wife');
      expect(res.reciprocal).toBe('Husband');
    });

    test('A (Female, Daughter) tags B as Father -> B sees A as Daughter', () => {
      const res = determineReciprocal({ assignedTag: 'Father', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Father');
      expect(res.reciprocal).toBe('Daughter');
    });

    test('A (Male, Son) tags B as Father -> B sees A as Son', () => {
      const res = determineReciprocal({ assignedTag: 'Father', actorGender: 'MALE' });
      expect(res.assigned).toBe('Father');
      expect(res.reciprocal).toBe('Son');
    });

    test('A (Female, Daughter) tags B as Mother -> B sees A as Daughter', () => {
      const res = determineReciprocal({ assignedTag: 'Mother', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Mother');
      expect(res.reciprocal).toBe('Daughter');
    });

    test('A (Male, Son) tags B as Mother -> B sees A as Son', () => {
      const res = determineReciprocal({ assignedTag: 'Mother', actorGender: 'MALE' });
      expect(res.assigned).toBe('Mother');
      expect(res.reciprocal).toBe('Son');
    });

    test('A (Female, Mother) tags B as Daughter -> B sees A as Mother', () => {
      const res = determineReciprocal({ assignedTag: 'Daughter', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Daughter');
      expect(res.reciprocal).toBe('Mother');
    });

    test('A (Male, Father) tags B as Daughter -> B sees A as Father', () => {
      const res = determineReciprocal({ assignedTag: 'Daughter', actorGender: 'MALE' });
      expect(res.assigned).toBe('Daughter');
      expect(res.reciprocal).toBe('Father');
    });

    test('A (Female, Mother) tags B as Son -> B sees A as Mother', () => {
      const res = determineReciprocal({ assignedTag: 'Son', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Son');
      expect(res.reciprocal).toBe('Mother');
    });

    test('A (Male, Father) tags B as Son -> B sees A as Father', () => {
      const res = determineReciprocal({ assignedTag: 'Son', actorGender: 'MALE' });
      expect(res.assigned).toBe('Son');
      expect(res.reciprocal).toBe('Father');
    });

    test('A (Female, Sister) tags B as Brother -> B sees A as Sister', () => {
      const res = determineReciprocal({ assignedTag: 'Brother', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Brother');
      expect(res.reciprocal).toBe('Sister');
    });

    test('A (Male, Brother) tags B as Brother -> B sees A as Brother', () => {
      const res = determineReciprocal({ assignedTag: 'Brother', actorGender: 'MALE' });
      expect(res.assigned).toBe('Brother');
      expect(res.reciprocal).toBe('Brother');
    });

    test('A (Female, Sister) tags B as Sister -> B sees A as Sister', () => {
      const res = determineReciprocal({ assignedTag: 'Sister', actorGender: 'FEMALE' });
      expect(res.assigned).toBe('Sister');
      expect(res.reciprocal).toBe('Sister');
    });

    test('A (Male, Brother) tags B as Sister -> B sees A as Brother', () => {
      const res = determineReciprocal({ assignedTag: 'Sister', actorGender: 'MALE' });
      expect(res.assigned).toBe('Sister');
      expect(res.reciprocal).toBe('Brother');
    });

    test('Symmetric tags: Best Friend -> Best Friend', () => {
      const res = determineReciprocal({ assignedTag: 'Best Friend' });
      expect(res.assigned).toBe('Best Friend');
      expect(res.reciprocal).toBe('Best Friend');
    });
  });

  // ==============================================================
  // 3. Database Persistence & API Bidirectional Synchronization
  // ==============================================================
  describe('3. Database Persistence & API Bidirectional Synchronization', () => {
    let daughterFatherConnId;
    let sisterBrotherConnId;
    let husbandWifeConnId;

    test('Husband & Wife: Husband tags Wife as Wife -> Wife sees Husband as Husband', async () => {
      const res = await request(app)
        .post('/api/v1/partner/request')
        .set('Authorization', `Bearer ${users.husband.token}`)
        .send({
          recipient_id: users.wife.id,
          relationship: 'Wife'
        });

      expect(res.status).toBe(201);
      husbandWifeConnId = res.body.connection.id;

      // Wife accepts
      await request(app)
        .post(`/api/v1/partner/requests/${husbandWifeConnId}/accept`)
        .set('Authorization', `Bearer ${users.wife.token}`);

      // Husband's contacts
      const hContacts = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.husband.token}`);
      const wifeContact = hContacts.body.contacts.find(c => c.user_id === users.wife.id);
      expect(wifeContact.relationship).toBe('Wife');

      // Wife's contacts
      const wContacts = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.wife.token}`);
      const husbandContact = wContacts.body.contacts.find(c => c.user_id === users.husband.id);
      expect(husbandContact.relationship).toBe('Husband');
    });

    test('Daughter connects to Father: creates reciprocal Daughter tag in DB automatically', async () => {
      const res = await request(app)
        .post('/api/v1/partner/request')
        .set('Authorization', `Bearer ${users.daughter.token}`)
        .send({
          recipient_id: users.father.id,
          relationship: 'Father'
        });

      expect(res.status).toBe(201);
      expect(res.body.success).toBe(true);
      daughterFatherConnId = res.body.connection.id;

      // Verify Supabase PostgreSQL row has both perspectives persisted
      const dbRow = await pool.query('SELECT * FROM partner_connections WHERE id = $1', [daughterFatherConnId]);
      expect(dbRow.rows[0].requester_relationship).toBe('Father');
      expect(dbRow.rows[0].recipient_relationship).toBe('Daughter');

      // Father accepts the connection
      const acceptRes = await request(app)
        .post(`/api/v1/partner/requests/${daughterFatherConnId}/accept`)
        .set('Authorization', `Bearer ${users.father.token}`);

      expect(acceptRes.status).toBe(200);
      expect(acceptRes.body.success).toBe(true);
    });

    test('Authoritative perspective in Contacts: Daughter sees Father as Father, Father sees Daughter as Daughter', async () => {
      // 1. Daughter's view of contacts
      const dContactsRes = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.daughter.token}`);

      expect(dContactsRes.status).toBe(200);
      const fatherContact = dContactsRes.body.contacts.find(c => c.user_id === users.father.id);
      expect(fatherContact).toBeDefined();
      expect(fatherContact.relationship).toBe('Father');

      // 2. Father's view of contacts
      const fContactsRes = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.father.token}`);

      expect(fContactsRes.status).toBe(200);
      const daughterContact = fContactsRes.body.contacts.find(c => c.user_id === users.daughter.id);
      expect(daughterContact).toBeDefined();
      expect(daughterContact.relationship).toBe('Daughter');
    });

    test('Updating relationship via Chat (POST /api/v1/chat/set-tag) atomically updates both perspectives', async () => {
      // Father in chat sets tag for Daughter to "Daughter 👧"
      const setTagRes = await request(app)
        .post('/api/v1/chat/set-tag')
        .set('Authorization', `Bearer ${users.father.token}`)
        .send({
          connection_id: daughterFatherConnId,
          tag: 'Daughter 👧'
        });

      expect(setTagRes.status).toBe(200);
      expect(setTagRes.body.success).toBe(true);
      expect(setTagRes.body.relationship).toBe('Daughter');
      expect(setTagRes.body.reciprocal_relationship).toBe('Father');

      // Verify Supabase database persistence
      const dbCheck = await pool.query('SELECT * FROM partner_connections WHERE id = $1', [daughterFatherConnId]);
      expect(dbCheck.rows[0].recipient_relationship).toBe('Daughter');
      expect(dbCheck.rows[0].requester_relationship).toBe('Father');

      // Verify audit event was logged
      const auditRes = await pool.query(
        `SELECT * FROM sharing_audit_events WHERE connection_id = $1 AND event_type = 'RELATIONSHIP_UPDATED'`,
        [daughterFatherConnId]
      );
      expect(auditRes.rows.length).toBeGreaterThan(0);
    });

    test('Sister connects to Brother: Brother sees Sister, Sister sees Brother', async () => {
      const reqRes = await request(app)
        .post('/api/v1/partner/request')
        .set('Authorization', `Bearer ${users.sister.token}`)
        .send({
          recipient_id: users.brother.id,
          relationship: 'Brother'
        });

      expect(reqRes.status).toBe(201);
      sisterBrotherConnId = reqRes.body.connection.id;

      await request(app)
        .post(`/api/v1/partner/requests/${sisterBrotherConnId}/accept`)
        .set('Authorization', `Bearer ${users.brother.token}`);

      // Sister contacts list
      const sisContacts = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.sister.token}`);
      const broContact = sisContacts.body.contacts.find(c => c.user_id === users.brother.id);
      expect(broContact.relationship).toBe('Brother');

      // Brother contacts list
      const broContacts = await request(app)
        .get('/api/v1/chat/contacts')
        .set('Authorization', `Bearer ${users.brother.token}`);
      const sisContact = broContacts.body.contacts.find(c => c.user_id === users.sister.id);
      expect(sisContact.relationship).toBe('Sister');
    });

    test('Incompatible explicit reciprocal pairing is rejected with 400 Bad Request', async () => {
      const badReq = await request(app)
        .put(`/api/v1/partner/connections/${daughterFatherConnId}/relationship`)
        .set('Authorization', `Bearer ${users.daughter.token}`)
        .send({
          relationship: 'Father',
          reciprocal_relationship: 'Wife' // Father cannot be paired with Wife!
        });

      expect(badReq.status).toBe(400);
      expect(badReq.body.success).toBe(false);
      expect(badReq.body.message).toMatch(/cannot be reciprocated as Wife/i);
    });

    test('Unauthorized user cannot modify connection relationship (404/403)', async () => {
      const unauthorizedRes = await request(app)
        .put(`/api/v1/partner/connections/${daughterFatherConnId}/relationship`)
        .set('Authorization', `Bearer ${users.stranger.token}`)
        .send({
          relationship: 'Best Friend'
        });

      expect([403, 404]).toContain(unauthorizedRes.status);
    });

    test('Revoking connection blocks health data access while preserving identity safety', async () => {
      // Daughter revokes Father's connection
      const revokeRes = await request(app)
        .delete(`/api/v1/partner/connections/${daughterFatherConnId}`)
        .set('Authorization', `Bearer ${users.daughter.token}`);

      expect(revokeRes.status).toBe(200);
      expect(revokeRes.body.success).toBe(true);

      // Verify Father cannot query Daughter's cycle status
      const statusRes = await request(app)
        .get(`/api/v1/partner/connections/${daughterFatherConnId}/member-status`)
        .set('Authorization', `Bearer ${users.father.token}`);

      expect(statusRes.status).toBe(403);
    });
  });
});
