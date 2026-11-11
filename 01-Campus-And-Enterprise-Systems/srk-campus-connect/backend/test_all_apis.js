const http = require('http');

const BASE_URL = 'http://127.0.0.1:5000';

function request(method, path, body = null, token = null) {
  return new Promise((resolve) => {
    const url = new URL(path, BASE_URL);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
      }
    };

    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
    }

    const startTime = Date.now();
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        const duration = Date.now() - startTime;
        let parsed = null;
        try {
          parsed = JSON.parse(data);
        } catch (e) {
          parsed = data;
        }
        resolve({
          status: res.statusCode,
          duration,
          data: parsed,
          raw: data
        });
      });
    });

    req.on('error', (err) => {
      resolve({
        status: 0,
        duration: Date.now() - startTime,
        error: err.message
      });
    });

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

async function runTestSuite() {
  console.log('\n============================================================');
  console.log('🏛️  SRK CAMPUS PLATFORM — COMPREHENSIVE END-TO-END API TEST');
  console.log('============================================================\n');

  let passed = 0;
  let failed = 0;
  const results = [];

  function logTest(name, method, endpoint, res, expectedStatuses = [200, 201]) {
    const isSuccess = expectedStatuses.includes(res.status);
    if (isSuccess) passed++;
    else failed++;

    const statusBadge = isSuccess ? '✅ PASS' : '❌ FAIL';
    const statusText = `[${res.status}] (${res.duration}ms)`;
    console.log(`${statusBadge} ${statusText.padEnd(16)} | ${method.padEnd(6)} ${endpoint.padEnd(35)} | ${name}`);
    if (!isSuccess) {
      console.log(`     ⚠️ Error Response: ${JSON.stringify(res.data || res.error)}`);
    }

    results.push({ name, method, endpoint, status: res.status, duration: res.duration, isSuccess });
  }

  // 1. PUBLIC HEALTH & TELEMETRY
  console.log('--- 1. PUBLIC & INFRASTRUCTURE ENDPOINTS ---');
  let res = await request('GET', '/api/v1/health');
  logTest('API Health Check', 'GET', '/api/v1/health', res);

  res = await request('GET', '/api/v1/audit/telemetry');
  logTest('Control Panel Telemetry Snapshot', 'GET', '/api/v1/audit/telemetry', res);

  // 2. AUTH FLOW & UID VERIFICATION
  console.log('\n--- 2. AUTHENTICATION & UID LIFECYCLE ---');
  res = await request('GET', '/api/v1/auth/uids');
  logTest('Fetch 30 Campus UIDs', 'GET', '/api/v1/auth/uids', res);

  res = await request('POST', '/api/v1/auth/send-otp', { uid: 'SRK-FAC-101' });
  logTest('Generate Verification OTP', 'POST', '/api/v1/auth/send-otp', res);

  // Sign up a test faculty UID if not already present
  res = await request('POST', '/api/v1/auth/signup-uid', {
    uid: 'SRK-FAC-101',
    email: 'fac101@srk.edu.in',
    password: 'Password@123',
    otp: '4821'
  });
  logTest('Sign Up / Activate Faculty UID', 'POST', '/api/v1/auth/signup-uid', res, [200, 201, 400]);

  // Login as Principal/Admin (SRK-ADM-001)
  res = await request('POST', '/api/v1/auth/login', {
    identifier: 'SRK-ADM-001',
    password: 'Password@123'
  });
  let adminToken = null;
  if (res.status === 200 && res.data?.data?.tokens?.accessToken) {
    adminToken = res.data.data.tokens.accessToken;
    logTest('Login as Super Admin / Principal (SRK-ADM-001)', 'POST', '/api/v1/auth/login', res);
  } else {
    // Try fallback signup
    await request('POST', '/api/v1/auth/signup-uid', {
      uid: 'SRK-ADM-001',
      email: 'admin001@srk.edu.in',
      password: 'Password@123',
      otp: '4821'
    });
    res = await request('POST', '/api/v1/auth/login', { identifier: 'SRK-ADM-001', password: 'Password@123' });
    adminToken = res.data?.data?.tokens?.accessToken;
    logTest('Login as Super Admin / Principal (SRK-ADM-001)', 'POST', '/api/v1/auth/login', res);
  }

  // Login as Faculty (SRK-FAC-101)
  res = await request('POST', '/api/v1/auth/login', {
    identifier: 'SRK-FAC-101',
    password: 'Password@123'
  });
  let facultyToken = res.data?.data?.tokens?.accessToken;
  logTest('Login as Faculty (SRK-FAC-101)', 'POST', '/api/v1/auth/login', res);

  // Test /auth/me with token
  res = await request('GET', '/api/v1/auth/me', null, adminToken);
  logTest('Get Current Authenticated User Profile', 'GET', '/api/v1/auth/me', res);

  // 3. CORE INSTITUTIONAL ENTITIES
  console.log('\n--- 3. ACADEMIC & INSTITUTIONAL ENTITIES ---');
  res = await request('GET', '/api/v1/departments', null, adminToken);
  logTest('Get Departments List', 'GET', '/api/v1/departments', res);

  res = await request('GET', '/api/v1/subjects', null, adminToken);
  logTest('Get Subjects List', 'GET', '/api/v1/subjects', res);

  res = await request('GET', '/api/v1/rooms', null, adminToken);
  logTest('Get Rooms / Cabins List', 'GET', '/api/v1/rooms', res);

  res = await request('GET', '/api/v1/faculty', null, adminToken);
  logTest('Get Faculty List', 'GET', '/api/v1/faculty', res);

  res = await request('GET', '/api/v1/students', null, adminToken);
  logTest('Get Students List', 'GET', '/api/v1/students', res);

  // 4. ADMIN & SEARCH
  console.log('\n--- 4. ADMIN & CAMPUS SEARCH ---');
  res = await request('GET', '/api/v1/admin/overview', null, adminToken);
  logTest('Get Admin Campus Overview', 'GET', '/api/v1/admin/overview', res);

  res = await request('GET', '/api/v1/admin/search?q=Faculty', null, adminToken);
  logTest('Search Campus Members', 'GET', '/api/v1/admin/search?q=Faculty', res);

  // 5. TIMETABLE & CLASS SESSIONS
  console.log('\n--- 5. TIMETABLES & CLASSES ---');
  res = await request('GET', '/api/v1/timetable', null, adminToken);
  logTest('Get Campus Timetable', 'GET', '/api/v1/timetable', res);

  res = await request('GET', '/api/v1/classes/current', null, facultyToken || adminToken);
  logTest('Get Current Active Class', 'GET', '/api/v1/classes/current', res);

  // 6. URGENT SUMMONS & NOTIFICATIONS
  console.log('\n--- 6. PRINCIPAL URGENT SUMMONS & PUSH NOTIFICATIONS ---');
  res = await request('POST', '/api/v1/meetings/test-summon-push', {
    targetFacultyUid: 'SRK-FAC-101',
    room: 'Principal Cabin P-01',
    reason: 'Emergency Coordination Review'
  });
  logTest('Trigger Principal Urgent Summon Push', 'POST', '/api/v1/meetings/test-summon-push', res);

  res = await request('GET', '/api/v1/meetings', null, adminToken);
  logTest('Get Campus Meetings / Summons', 'GET', '/api/v1/meetings', res);

  // 7. ANALYTICS & AUDIT LOGS
  console.log('\n--- 7. ANALYTICS & AUDIT SYSTEM ---');
  res = await request('GET', '/api/v1/analytics/overview', null, adminToken);
  logTest('Analytics Campus Overview', 'GET', '/api/v1/analytics/overview', res);

  res = await request('GET', '/api/v1/analytics/presence', null, adminToken);
  logTest('Analytics Presence Metrics', 'GET', '/api/v1/analytics/presence', res);

  res = await request('GET', '/api/v1/leaves', null, adminToken);
  logTest('Faculty Leaves Overview', 'GET', '/api/v1/leaves', res);

  res = await request('GET', '/api/v1/audit/logs', null, adminToken);
  logTest('Institutional Audit Logs', 'GET', '/api/v1/audit/logs', res);

  console.log('\n============================================================');
  console.log(`📊 TEST SUITE SUMMARY: ${passed} PASSED / ${failed} FAILED (${Math.round((passed / (passed + failed)) * 100)}% SUCCESS RATE)`);
  console.log('============================================================\n');
}

runTestSuite();
