// test/full_api_suite.test.js
// Automated End-to-End API Test Suite for ProjectFlow Intelligence
// Tests all 54 endpoints against local or Render backend server.

const http = require('http');
const https = require('https');
const { URL } = require('url');

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8082';
console.log(`\n======================================================================`);
console.log(`     PROJECTFLOW INTELLIGENCE — FULL API REGRESSION TEST SUITE`);
console.log(`======================================================================`);
console.log(`Target Server: ${BASE_URL}\n`);

let passedCount = 0;
let failedCount = 0;
const results = [];

function makeRequest(method, path, body = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const fullUrl = new URL(path, BASE_URL);
    const isHttps = fullUrl.protocol === 'https:';
    const lib = isHttps ? https : http;

    const payload = body ? JSON.stringify(body) : null;
    const reqHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer test-admin-token',
      ...headers
    };
    if (payload) {
      reqHeaders['Content-Length'] = Buffer.byteLength(payload);
    }

    const req = lib.request(fullUrl, {
      method,
      headers: reqHeaders,
      timeout: 10000
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        let parsed = null;
        try {
          parsed = JSON.parse(data);
        } catch {
          parsed = data;
        }
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: parsed
        });
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timed out after 10000ms'));
    });

    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

async function testEndpoint(testName, method, path, body = null, expectedStatus = [200, 201]) {
  const allowed = Array.isArray(expectedStatus) ? expectedStatus : [expectedStatus];
  try {
    const start = Date.now();
    const res = await makeRequest(method, path, body);
    const duration = Date.now() - start;

    if (allowed.includes(res.statusCode)) {
      passedCount++;
      console.log(`  ✔ [PASS] [${res.statusCode}] ${method} ${path} (${duration}ms) — ${testName}`);
      results.push({ name: testName, method, path, status: res.statusCode, passed: true, duration });
      return res.body;
    } else {
      failedCount++;
      console.error(`  ✖ [FAIL] [${res.statusCode}] ${method} ${path} (${duration}ms) — Expected: ${allowed.join('/')}, Got: ${res.statusCode}`);
      results.push({ name: testName, method, path, status: res.statusCode, passed: false, duration, error: res.body });
      return null;
    }
  } catch (err) {
    failedCount++;
    console.error(`  ✖ [ERR ] ${method} ${path} — Error: ${err.message}`);
    results.push({ name: testName, method, path, status: 0, passed: false, duration: 0, error: err.message });
    return null;
  }
}

async function runAllTests() {
  console.log(`--- [GROUP 1: Authentication & User Session] ---`);
  const loginRes = await testEndpoint('Auth Login (admin)', 'POST', '/api/v1/auth/login', { email: 'admin@projectflow.io', password: 'ProjectFlow@2026' });
  await testEndpoint('Auth Signup (new session)', 'POST', '/api/v1/auth/signup', { email: `test_${Date.now()}@projectflow.io`, fullName: 'Test User' });
  await testEndpoint('Get Current Profile (/me)', 'GET', '/api/v1/me');
  await testEndpoint('Update Display Profile (/me/profile)', 'PATCH', '/api/v1/me/profile', { fullName: 'System Administrator' });
  await testEndpoint('Register Mobile FCM Token', 'POST', '/api/v1/users/fcm-token', { fcmToken: 'test_fcm_token_sample_123', email: 'admin@projectflow.io' });
  await testEndpoint('Device Heartbeat Ping', 'POST', '/api/v1/users/heartbeat', { email: 'admin@projectflow.io' });

  console.log(`\n--- [GROUP 2: Admin Overview & User RBAC Management] ---`);
  await testEndpoint('Admin Global Overview Metrics', 'GET', '/api/v1/admin/overview');
  await testEndpoint('List All Admin Users', 'GET', '/api/v1/admin/users');
  const newUser = await testEndpoint('Invite New Member', 'POST', '/api/v1/admin/users', { email: `member_${Date.now()}@projectflow.io`, fullName: 'Invited Member', role: 'MEMBER' });
  const userId = newUser ? newUser.id : '00000000-0000-0000-0000-000000000003';
  await testEndpoint('Update User Role (MANAGER)', 'PATCH', `/api/v1/admin/users/${userId}/role`, { role: 'MANAGER' });
  await testEndpoint('Toggle User Account Status', 'PATCH', `/api/v1/admin/users/${userId}/status`, { active: false });

  console.log(`\n--- [GROUP 3: Workspaces & Projects Management] ---`);
  const workspaces = await testEndpoint('List Workspaces', 'GET', '/api/v1/workspaces');
  const wsId = workspaces && workspaces.length ? workspaces[0].id : '00000000-0000-0000-0000-000000000001';
  await testEndpoint('Create Workspace', 'POST', '/api/v1/workspaces', { name: `Workspace_${Date.now().toString().slice(-4)}`, slug: `ws-${Date.now()}` });
  await testEndpoint('List Admin Workspaces', 'GET', '/api/v1/admin/workspaces');
  const projects = await testEndpoint('List Admin Projects', 'GET', '/api/v1/admin/projects');
  await testEndpoint('List All Projects (/projects)', 'GET', '/api/v1/projects');
  await testEndpoint('List Workspace Projects', 'GET', `/api/v1/workspaces/${wsId}/projects`);
  const newProj = await testEndpoint('Create Project in Workspace', 'POST', `/api/v1/workspaces/${wsId}/projects`, { name: `Project ${Date.now().toString().slice(-4)}`, code: `PRJ-${Date.now().toString().slice(-3)}`, description: 'Test Project' });
  const projId = newProj ? newProj.id : (projects && projects.length ? projects[0].id : '10000000-0000-0000-0000-000000000001');
  await testEndpoint('Update Project Metadata (PATCH)', 'PATCH', `/api/v1/projects/${projId}`, { status: 'IN_PROGRESS', health: 'ON_TRACK', targetDate: '2026-12-31' });

  console.log(`\n--- [GROUP 4: Tasks, Workflow & Interactive Kanban] ---`);
  await testEndpoint('List Project Tasks', 'GET', `/api/v1/projects/${projId}/tasks`);
  const allTasks = await testEndpoint('List All Tasks (/tasks)', 'GET', '/api/v1/tasks');
  const newTask = await testEndpoint('Create Project Task', 'POST', `/api/v1/projects/${projId}/tasks`, { title: 'Automated Test Task', priority: 'HIGH', dueDate: '2026-11-15' });
  const taskId = newTask ? newTask.id : (allTasks && allTasks.length ? allTasks[0].id : '20000000-0000-0000-0000-000000000001');
  await testEndpoint('Update Task Status (IN_PROGRESS, 50%)', 'PATCH', `/api/v1/tasks/${taskId}/status`, { statusCategory: 'IN_PROGRESS', progressPercent: 50 });
  await testEndpoint('Update Task Status (DONE, 100%)', 'PATCH', `/api/v1/tasks/${taskId}/status`, { statusCategory: 'DONE', progressPercent: 100 });

  console.log(`\n--- [GROUP 5: Teams, Squads & Collaboration] ---`);
  await testEndpoint('Get Team Members Roster (/team)', 'GET', '/api/v1/team');
  await testEndpoint('Get Squad Teams (/teams)', 'GET', '/api/v1/teams');
  await testEndpoint('Create Squad Team', 'POST', '/api/v1/teams', { name: `Squad_${Date.now().toString().slice(-4)}`, description: 'Test Squad' });

  console.log(`\n--- [GROUP 6: WhatsApp-Style Discussions & Direct Chats] ---`);
  await testEndpoint('Get Chat Groups', 'GET', '/api/v1/chat/groups');
  const newGroup = await testEndpoint('Create Chat Group (Admin only)', 'POST', '/api/v1/chat/groups', { name: `Channel ${Date.now().toString().slice(-4)}`, creatorRole: 'ADMINISTRATOR' });
  const channel = newGroup ? newGroup.channel : 'general';
  await testEndpoint('Fetch Chat Messages', 'GET', `/api/v1/chat/messages?channel=${channel}`);
  const sentMsg = await testEndpoint('Post Chat Message', 'POST', '/api/v1/chat/messages', { channel, content: 'Automated test message', senderName: 'System Test' });
  const msgId = sentMsg ? sentMsg.id : 'msg_1';
  await testEndpoint('React to Chat Message', 'POST', `/api/v1/chat/messages/${msgId}/react`, { emoji: '🚀' });

  console.log(`\n--- [GROUP 7: Push Notifications & Broadcast Dispatcher] ---`);
  await testEndpoint('List In-App Notifications', 'GET', '/api/v1/notifications');
  await testEndpoint('Mark All Notifications Read', 'POST', '/api/v1/notifications/mark-all-read');
  await testEndpoint('Send Targeted Push Alert', 'POST', '/api/v1/notifications/send-push', { title: 'Test Alert', message: 'Regression test execution', priority: 'HIGH' });
  await testEndpoint('Send Broadcast Push Notification', 'POST', '/api/v1/broadcast/send', { title: 'Broadcast Test', message: 'All-hands alert' });
  await testEndpoint('Get Push Broadcast Delivery Logs', 'GET', '/api/v1/broadcast/history');

  console.log(`\n--- [GROUP 8: Deterministic Risk Radar & Simulation] ---`);
  await testEndpoint('Get Project Risk Findings', 'GET', `/api/v1/projects/${projId}/risks`);
  await testEndpoint('Trigger Risk Evaluation Engine', 'POST', `/api/v1/projects/${projId}/risks/evaluate`);
  await testEndpoint('What-If Scenario Simulation', 'POST', '/api/v1/scenarios/simulate', {
    projectId: projId,
    scenarioName: 'Rush Delivery',
    changes: [{ taskId, proposedDueDate: '2026-10-25' }]
  });

  console.log(`\n--- [GROUP 9: App Releases & APK Distribution Portal] ---`);
  await testEndpoint('Get Latest Published Release (/releases/latest)', 'GET', '/api/v1/releases/latest');
  const allReleases = await testEndpoint('List Admin Releases', 'GET', '/api/v1/admin/releases');
  const relId = allReleases && allReleases.length ? allReleases[0].id : '50000000-0000-0000-0000-000000000001';
  await testEndpoint('Publish Release Artifact', 'POST', `/api/v1/admin/releases/${relId}/publish`);
  await testEndpoint('Unpublish Release Artifact', 'POST', `/api/v1/admin/releases/${relId}/unpublish`);
  await testEndpoint('Re-publish Release Artifact', 'POST', `/api/v1/admin/releases/${relId}/publish`);

  console.log(`\n--- [GROUP 10: Security Audit Trail & System Telemetry] ---`);
  await testEndpoint('Fetch Paginated Audit Logs', 'GET', '/api/v1/admin/audit-events?page=0&size=10');
  await testEndpoint('Search Audit Logs by Action Filter', 'GET', '/api/v1/admin/audit-events?action=SETTINGS_UPDATED');
  await testEndpoint('System Health Probes (/admin/system/health)', 'GET', '/api/v1/admin/system/health');
  const errLog = await testEndpoint('Log Client Telemetry Error', 'POST', '/api/v1/telemetry/errors', { severity: 'WARNING', message: 'Test telemetry event', source: 'TEST_RUNNER' });
  await testEndpoint('Fetch System Error Logs', 'GET', '/api/v1/admin/system/errors');
  if (errLog && errLog.id) {
    await testEndpoint('Resolve System Error Entry', 'PATCH', `/api/v1/admin/system/errors/${errLog.id}/resolve`);
  }

  console.log(`\n--- [GROUP 11: Enterprise System Settings & Reports] ---`);
  await testEndpoint('Fetch Persisted System Settings', 'GET', '/api/v1/admin/settings');
  await testEndpoint('Update System Settings (PATCH)', 'PATCH', '/api/v1/admin/settings', { organizationName: 'ProjectFlow Enterprise', syncIntervalMinutes: 15 });
  await testEndpoint('Generate Real-Time Analytics Summary', 'GET', '/api/v1/reports/summary');

  console.log(`\n======================================================================`);
  console.log(`                     API TEST RESULTS SUMMARY`);
  console.log(`======================================================================`);
  console.log(`Total Endpoints Tested: ${results.length}`);
  console.log(`Passed:                 ${passedCount} ✔`);
  console.log(`Failed:                 ${failedCount} ✖`);
  console.log(`Pass Rate:               ${((passedCount / results.length) * 100).toFixed(1)}%`);
  console.log(`======================================================================\n`);

  if (failedCount > 0) {
    process.exit(1);
  }
}

runAllTests().catch(err => {
  console.error('[FATAL TEST SUITE FAILURE]', err);
  process.exit(1);
});
