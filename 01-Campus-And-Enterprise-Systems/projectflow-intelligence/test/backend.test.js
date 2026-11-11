const assert = require('node:assert');
const { hasCycle } = require('../src/engine/dependencyValidator');
const { evaluateProjectRisks } = require('../src/engine/deterministicRiskEngine');
const { evaluateScenario } = require('../src/engine/whatIfSchedulingEngine');

console.log('🧪 Starting ProjectFlow Intelligence Engine Unit Tests...');

// 1. DependencyValidator tests
console.log('\n--- 1. Testing DependencyValidator (DAG & Cycles) ---');
const taskIds = ['t1', 't2', 't3'];

// No cycle: t1 -> t2 -> t3
const validDeps = [
  { predecessorTaskId: 't1', taskId: 't2' },
  { predecessorTaskId: 't2', taskId: 't3' }
];
assert.strictEqual(hasCycle(taskIds, validDeps), false, 'Linear deps should not have cycles');
console.log('✔ Cycle detection negative case passed (no cycle in linear DAG)');

// With cycle: t1 -> t2 -> t3 -> t1
const cyclicDeps = [
  { predecessorTaskId: 't1', taskId: 't2' },
  { predecessorTaskId: 't2', taskId: 't3' },
  { predecessorTaskId: 't3', taskId: 't1' }
];
assert.strictEqual(hasCycle(taskIds, cyclicDeps), true, 'Cyclic deps should be detected');
console.log('✔ Cycle detection positive case passed (cycle detected)');

// 2. DeterministicRiskEngine tests
console.log('\n--- 2. Testing DeterministicRiskEngine (Mathematical Rules) ---');
const project = { id: 'p1', name: 'Project Alpha', targetCompletionDate: '2026-12-31' };
const overdueTask = {
  id: 't-overdue',
  title: 'Database Setup',
  status: 'IN_PROGRESS',
  dueDate: '2020-01-01',
  estimatedHours: 10,
  completedAt: null
};
const normalTask = {
  id: 't-normal',
  title: 'Documentation',
  status: 'TODO',
  dueDate: '2029-01-01',
  estimatedHours: 5,
  completedAt: null
};

const risks = evaluateProjectRisks(project, [overdueTask, normalTask], []);
assert(risks.some(r => r.ruleId === 'OVERDUE_TASK' && r.affectedEntityId === 't-overdue'), 'Must identify overdue task risk');
console.log('✔ Deterministic risk engine detected OVERDUE_TASK rule');

// 3. WhatIfSchedulingEngine tests
console.log('\n--- 3. Testing WhatIfSchedulingEngine ---');
const currentTasks = [
  { id: 't1', title: 'Task 1', dueDate: '2026-11-01', estimatedHours: 8 },
  { id: 't2', title: 'Task 2', dueDate: '2026-11-10', estimatedHours: 16 }
];
const scenario = {
  id: 'sc-1',
  name: 'Deadline Extension',
  changes: [
    { taskId: 't2', proposedDueDate: '2026-11-20', proposedEstimatedHours: 20 }
  ]
};
const scenarioResult = evaluateScenario(project, currentTasks, validDeps, scenario);
assert(scenarioResult.valid === true, 'Scenario evaluation should be valid');
assert.strictEqual(scenarioResult.scenarioFinishDate, '2026-11-20', 'Scenario finish date should reflect proposed due date');
console.log('✔ What-If scenario evaluation computed expected finish date: ' + scenarioResult.scenarioFinishDate);

// 4. Application Release Verification
console.log('\n--- 4. Testing Application Release Verification ---');
const fs = require('node:fs');
const crypto = require('node:crypto');
const releaseApkPath = 'releases/android/ProjectFlow-Intelligence-v2.0.0.apk';
assert(fs.existsSync(releaseApkPath), 'Official release APK artifact must exist in storage path');
const apkBuffer = fs.readFileSync(releaseApkPath);
const hash = crypto.createHash('sha256').update(apkBuffer).digest('hex');
assert.strictEqual(hash, 'b0ba8582d3c3bd3c6a38a6779c045e7d19e7a43cd4a7b1ec5fd321e778d50651', 'Release APK checksum must match cryptographic hash');
console.log('✔ Official APK release artifact verified on disk with valid SHA-256: ' + hash);

console.log('\n🎉 ALL PROJECTFLOW INTELLIGENCE BACKEND TESTS PASSED SUCCESSFULLY!\n');
