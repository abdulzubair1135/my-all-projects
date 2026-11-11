const { test, describe, before, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const fs = require('fs');

// Set temporary test DB
process.env.DATABASE_PATH = path.resolve(__dirname, '../../data/test_agent.sqlite');
process.env.WORKSPACE_ROOT = path.resolve(__dirname, '../../workspace/test_workspace');

const { db } = require('../src/database/db');
const projectService = require('../src/services/projectService');
const fileService = require('../src/services/fileService');

describe('Backend Services & Persistence', () => {
  let testProject;

  before(async () => {
    await db.ready;
    testProject = projectService.createProject('test-project', 'Build an expense app');
  });

  after(() => {
    if (testProject) {
      projectService.deleteProject(testProject.id);
    }
    // Cleanup test database
    if (fs.existsSync(process.env.DATABASE_PATH)) {
      try { fs.unlinkSync(process.env.DATABASE_PATH); } catch {}
    }
    if (fs.existsSync(process.env.WORKSPACE_ROOT)) {
      try { fs.rmSync(process.env.WORKSPACE_ROOT, { recursive: true, force: true }); } catch {}
    }
  });

  test('Project creation and retrieval', () => {
    assert.ok(testProject.id, 'Project ID should exist');
    assert.strictEqual(testProject.name, 'test-project');
    const retrieved = projectService.getProject(testProject.id);
    assert.strictEqual(retrieved.id, testProject.id);
  });

  test('File write, read, and conflict detection', () => {
    const filePath = 'src/test.txt';
    const content = 'Hello World';

    const saveRes = fileService.saveFile(testProject.id, filePath, content);
    assert.ok(saveRes.hash, 'Hash should be generated');

    const readRes = fileService.getContent(testProject.id, filePath);
    assert.strictEqual(readRes.content, content);
    assert.strictEqual(readRes.hash, saveRes.hash);

    // Conflict detection with wrong expected hash
    assert.throws(() => {
      fileService.saveFile(testProject.id, filePath, 'New content', 'wrong_hash_123');
    }, /Conflict detected/);
  });

  test('Path traversal rejection', () => {
    assert.throws(() => {
      fileService.resolveSafePath(testProject.path, '../../../../Windows/System32');
    }, /Path traversal detected/);

    assert.throws(() => {
      fileService.resolveSafePath(testProject.path, 'CON.txt');
    }, /Invalid path: reserved/);
  });
});
