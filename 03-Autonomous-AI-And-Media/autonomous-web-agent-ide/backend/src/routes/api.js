const express = require('express');
const router = express.Router();
const path = require('path');
const { db } = require('../database/db');
const projectService = require('../services/projectService');
const fileService = require('../services/fileService');
const fileWatcher = require('../services/fileWatcher');
const processManager = require('../services/processManager');
const agentBridge = require('../services/agentBridge');
const eventBus = require('../services/eventBus');
const uploadService = require('../services/uploadService');

// Multer setup for file uploads (memory storage — we handle writing manually)
let multer;
let upload;
try {
  multer = require('multer');
  upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 50 * 1024 * 1024 }, // 50MB max
    fileFilter: (req, file, cb) => {
      // Accept images and ZIPs
      const allowed = /\.(png|jpg|jpeg|webp|gif|bmp|svg|zip)$/i;
      if (allowed.test(path.extname(file.originalname))) {
        cb(null, true);
      } else {
        cb(new Error(`File type not allowed: ${path.extname(file.originalname)}`));
      }
    },
  });
} catch {
  // multer not installed — upload endpoints will return 503
  upload = null;
}

// 1. Health check
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    backend: true,
    database: true,
    agentBridge: agentBridge.getStatus()
  });
});

// 2. Projects
router.get('/projects', (req, res) => {
  try {
    const list = projectService.listProjects();
    res.json(list);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/projects', (req, res) => {
  try {
    const { name, prompt } = req.body;
    if (!name || typeof name !== 'string') {
      return res.status(400).json({ error: 'Project name is required' });
    }
    const project = projectService.createProject(name, prompt || '');
    fileWatcher.watchProject(project);
    res.status(201).json(project);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/projects/:id', (req, res) => {
  try {
    const project = projectService.getProject(req.params.id);
    if (!project) return res.status(404).json({ error: 'Project not found' });
    fileWatcher.watchProject(project);
    res.json(project);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.delete('/projects/:id', (req, res) => {
  try {
    processManager.stopAllForProject(req.params.id);
    const success = projectService.deleteProject(req.params.id);
    if (!success) return res.status(404).json({ error: 'Project not found' });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/projects/:id/zip', (req, res) => {
  try {
    const { zipPath, fileName } = fileService.createProjectZip(req.params.id);
    res.download(zipPath, fileName, (err) => {
      try {
        const fs = require('fs');
        if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);
      } catch {}
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/browser/show', (req, res) => {
  try {
    const { spawn, execSync } = require('child_process');
    const path = require('path');
    const fs = require('fs');

    const provider = req.body?.provider || req.query?.provider || 'gemini_web';
    
    // 1. Try to restore and focus any existing Chrome/Chromium window
    const psCmd = `powershell -NoProfile -Command "
      Add-Type -TypeDefinition @'
      using System;
      using System.Runtime.InteropServices;
      public class WinAct {
        [DllImport(\\"user32.dll\\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        [DllImport(\\"user32.dll\\")] public static extern bool SetForegroundWindow(IntPtr hWnd);
      }
'@ -ErrorAction SilentlyContinue;
      $found = $false;
      Get-Process -Name 'chrome','chromium' -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.MainWindowHandle -ne [IntPtr]::Zero) {
          [WinAct]::ShowWindow($_.MainWindowHandle, 9);
          [WinAct]::SetForegroundWindow($_.MainWindowHandle);
          $found = $true;
        }
      };
      if (-not $found) { exit 1 }
    "`;

    let broughtToFront = false;
    try {
      execSync(psCmd, { stdio: 'ignore', timeout: 1500 });
      broughtToFront = true;
    } catch {}

    // 2. If no existing window brought to front, launch live_browser.py!
    let launched = false;
    if (!broughtToFront) {
      const rootDir = path.resolve(__dirname, '../../..');
      const agentDir = path.join(rootDir, 'agent');
      let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
      const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
      if (fs.existsSync(venvWin)) pythonBin = venvWin;

      const liveScript = path.join(agentDir, 'browser', 'live_browser.py');
      const child = spawn(pythonBin, [liveScript, provider], {
        cwd: agentDir,
        detached: true,
        stdio: 'ignore'
      });
      child.unref();
      launched = true;
    }

    res.json({ success: true, broughtToFront, launched });
  } catch (err) {
    res.json({ success: false, error: err.message });
  }
});

// 3. Agent Lifecycle & Controls
router.get('/agent/status', (req, res) => {
  res.json(agentBridge.getStatus());
});

router.post('/agent/start', (req, res) => {
  try {
    const { projectId, prompt, approvalMode, provider, imagePaths, images } = req.body;
    if (!projectId || !prompt) {
      return res.status(400).json({ error: 'projectId and prompt are required' });
    }
    const result = agentBridge.startAgent(projectId, prompt, {
      approvalMode,
      provider,
      imagePaths: imagePaths || images
    });
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/agent/pause', (req, res) => {
  const success = agentBridge.pauseAgent();
  res.json({ success });
});

router.post('/agent/resume', (req, res) => {
  const success = agentBridge.resumeAgent();
  res.json({ success });
});

router.post('/agent/stop', (req, res) => {
  const success = agentBridge.stopAgent();
  res.json({ success });
});

router.post('/agent/override', (req, res) => {
  const { prompt } = req.body;
  if (!prompt) return res.status(400).json({ error: 'Prompt is required' });
  const success = agentBridge.overrideAgent(prompt);
  res.json({ success });
});

router.get('/agent/tasks', (req, res) => {
  const { projectId } = req.query;
  if (!projectId) return res.status(400).json({ error: 'projectId is required' });
  const tasks = db.prepare('SELECT * FROM tasks WHERE project_id = ? ORDER BY order_index ASC').all(projectId);
  const dependencies = db.prepare(`
    SELECT td.* FROM task_dependencies td
    JOIN tasks t ON td.task_id = t.id
    WHERE t.project_id = ?
  `).all(projectId);

  res.json({ tasks, dependencies });
});

router.get('/agent/events', (req, res) => {
  const { projectId, limit = 100 } = req.query;
  if (projectId) {
    const events = db.prepare('SELECT * FROM agent_events WHERE project_id = ? ORDER BY id DESC LIMIT ?').all(projectId, limit);
    return res.json(events.reverse());
  }
  const events = db.prepare('SELECT * FROM agent_events ORDER BY id DESC LIMIT ?').all(limit);
  res.json(events.reverse());
});

// 4. File Management
router.get('/files/tree', (req, res) => {
  try {
    const { projectId } = req.query;
    if (!projectId) return res.status(400).json({ error: 'projectId is required' });
    const tree = fileService.getTree(projectId);
    res.json(tree);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get('/files/content', (req, res) => {
  try {
    const { projectId, path: filePath } = req.query;
    if (!projectId || !filePath) return res.status(400).json({ error: 'projectId and path are required' });
    const fileData = fileService.getContent(projectId, filePath);
    res.json(fileData);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/files/save', (req, res) => {
  try {
    const { projectId, path: filePath, content, expectedHash } = req.body;
    if (!projectId || !filePath || content === undefined) {
      return res.status(400).json({ error: 'projectId, path, and content are required' });
    }
    const result = fileService.saveFile(projectId, filePath, content, expectedHash);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/files/mkdir', (req, res) => {
  try {
    const { projectId, path: dirPath } = req.body;
    if (!projectId || !dirPath) return res.status(400).json({ error: 'projectId and path are required' });
    const result = fileService.createDirectory(projectId, dirPath);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.delete('/files/delete', (req, res) => {
  try {
    const projectId = req.body?.projectId || req.query?.projectId;
    const targetPath = req.body?.path || req.query?.path || req.body?.filePath || req.query?.filePath;
    if (!projectId || !targetPath) return res.status(400).json({ error: 'projectId and path are required' });
    const result = fileService.deleteFile(projectId, targetPath);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/files/delete', (req, res) => {
  try {
    const projectId = req.body?.projectId || req.query?.projectId;
    const targetPath = req.body?.path || req.query?.path || req.body?.filePath || req.query?.filePath;
    if (!projectId || !targetPath) return res.status(400).json({ error: 'projectId and path are required' });
    const result = fileService.deleteFile(projectId, targetPath);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get('/files/search', (req, res) => {
  try {
    const { projectId, q } = req.query;
    if (!projectId || !q) return res.status(400).json({ error: 'projectId and q query are required' });
    const results = fileService.searchFiles(projectId, q);
    res.json(results);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 5. Background Processes
router.get('/processes', (req, res) => {
  const { projectId } = req.query;
  const list = processManager.listProcesses(projectId);
  res.json(list);
});

router.post('/processes/run', (req, res) => {
  const { projectId, command, name } = req.body;
  if (!projectId || !command) return res.status(400).json({ error: 'projectId and command required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });
  try {
    const proc = processManager.startProcess(projectId, name || 'terminal_cmd', command, [], project.path);
    res.json({ success: true, process: proc });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/processes/:id/stop', (req, res) => {
  const success = processManager.stopProcess(req.params.id);
  res.json({ success });
});

// 6. Settings
router.get('/settings', (req, res) => {
  const settings = db.prepare('SELECT * FROM settings').all();
  const map = {};
  settings.forEach(s => {
    try { map[s.key] = JSON.parse(s.value); } catch { map[s.key] = s.value; }
  });
  res.json(map);
});

router.post('/settings', (req, res) => {
  const entries = Object.entries(req.body);
  const now = new Date().toISOString();
  const upsert = db.prepare(`
    INSERT INTO settings (key, value, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
  `);

  const tx = db.transaction((list) => {
    for (const [k, v] of list) {
      upsert.run(k, typeof v === 'object' ? JSON.stringify(v) : String(v), now);
      if (k === 'approvalMode') {
        agentBridge.setApprovalMode(v);
      }
    }
  });

  tx(entries);
  res.json({ success: true });
});

// 7. Approvals
router.get('/approvals', (req, res) => {
  const { projectId } = req.query;
  if (projectId) {
    const list = db.prepare("SELECT * FROM approvals WHERE project_id = ? AND status = 'PENDING' ORDER BY created_at DESC").all(projectId);
    return res.json(list);
  }
  const list = db.prepare("SELECT * FROM approvals WHERE status = 'PENDING' ORDER BY created_at DESC").all();
  res.json(list);
});

router.post('/approvals/:id/approve', (req, res) => {
  const { alwaysAllow } = req.body;
  const decision = alwaysAllow ? 'ALWAYS_ALLOW' : 'APPROVE';
  const success = agentBridge.sendApprovalResponse(req.params.id, decision);
  res.json({ success });
});

router.post('/approvals/:id/reject', (req, res) => {
  const success = agentBridge.sendApprovalResponse(req.params.id, 'REJECT');
  res.json({ success });
});

// 9. AI Evolution & Cognitive Training Lab
const evolutionService = require('../services/evolutionService');

router.get('/evolution/stats', (req, res) => {
  try {
    const stats = evolutionService.getStats();
    res.json(stats);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/evolution/train', async (req, res) => {
  try {
    const { topic } = req.body || {};
    const result = await evolutionService.trainTopic(topic);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 10. Human Review Feedback & AI Emotion Reinforcement Loop
const reviewFeedbackService = require('../services/reviewFeedbackService');

router.get('/reviews/stats', (req, res) => {
  try {
    const stats = reviewFeedbackService.getStats();
    res.json(stats);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/reviews/submit', async (req, res) => {
  try {
    const { projectId, sentiment, comment } = req.body;
    const result = await reviewFeedbackService.submitReview(projectId, sentiment, comment);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 11. Autonomous Docker & Database Provisioner
const dockerService = require('../services/dockerService');

router.get('/docker/status', (req, res) => {
  try {
    const status = dockerService.getStatus();
    res.json(status);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/docker/start-db', async (req, res) => {
  try {
    const { type = 'mongodb', port = 27017 } = req.body;
    const result = await dockerService.ensureDatabaseContainer(type, port);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── 12. Autonomous Web-Agent IDE: File Uploads (Images + ZIP Import) ─────────

// Upload 1 or more images for a project
router.post('/uploads/image', (req, res) => {
  if (!upload) return res.status(503).json({ error: 'multer not installed. Run: npm install multer' });
  upload.array('images', 10)(req, res, async (err) => {
    if (err) return res.status(400).json({ error: err.message });
    try {
      const { projectId } = req.body;
      if (!projectId) return res.status(400).json({ error: 'projectId required' });
      if (!req.files || req.files.length === 0) return res.status(400).json({ error: 'No files uploaded' });

      const saved = [];
      for (const file of req.files) {
        const result = uploadService.saveImage(projectId, file.originalname, file.buffer);
        saved.push(result);
      }
      res.json({ success: true, uploaded: saved });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });
});

// Import a ZIP file — extract into project workspace
router.post('/uploads/zip', (req, res) => {
  if (!upload) return res.status(503).json({ error: 'multer not installed. Run: npm install multer' });
  upload.single('zip')(req, res, async (err) => {
    if (err) return res.status(400).json({ error: err.message });
    try {
      const { projectId } = req.body;
      if (!projectId) return res.status(400).json({ error: 'projectId required' });
      if (!req.file) return res.status(400).json({ error: 'No ZIP file uploaded' });
      if (!req.file.originalname.toLowerCase().endsWith('.zip')) {
        return res.status(400).json({ error: 'Only .zip files accepted' });
      }

      const result = await uploadService.extractZip(projectId, req.file.buffer);
      
      // Notify frontend via WebSocket
      eventBus.emit('file.tree.changed', { projectId });
      
      res.json({ success: true, ...result });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });
});

// List uploaded images for a project
router.get('/uploads/:projectId/images', (req, res) => {
  try {
    const list = uploadService.listUploads(req.params.projectId);
    res.json(list);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Delete an uploaded image
router.delete('/uploads/:projectId/images/:fileName', (req, res) => {
  try {
    const result = uploadService.deleteUpload(req.params.projectId, req.params.fileName);
    res.json(result);
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// Serve uploaded images as static files (for previews)
router.get('/uploads/:projectId/images/:fileName/preview', (req, res) => {
  try {
    const list = uploadService.listUploads(req.params.projectId);
    const file = list.find(f => f.fileName === req.params.fileName);
    if (!file) return res.status(404).json({ error: 'Not found' });
    res.sendFile(file.fullPath);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ── 13. Error Memory Stats ─────────────────────────────────────────────────────
router.get('/agent/memory/errors', (req, res) => {
  const { projectId } = req.query;
  if (!projectId) return res.status(400).json({ error: 'projectId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const path = require('path');
  const { execFile } = require('child_process');
  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');

  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  execFile(pythonBin, [cliScript, 'list-errors', project.path], { timeout: 10000 }, (err, stdout) => {
    if (err) return res.json({ entries: [] });
    try {
      res.json({ entries: JSON.parse(stdout.trim()) });
    } catch {
      res.json({ entries: [] });
    }
  });
});

// ── 14. Environment Doctor ──────────────────────────────────────────────────
router.get('/doctor', (req, res) => {
  const { execSync } = require('child_process');
  const checkCmd = (cmd) => {
    try {
      return execSync(cmd, { timeout: 3000, stdio: ['pipe', 'pipe', 'pipe'] }).toString().trim().split('\n')[0];
    } catch {
      return null;
    }
  };

  const report = {
    overall_status: 'HEALTHY',
    tools: {
      node: { installed: true, version: process.version },
      python: { installed: Boolean(checkCmd('python --version')), version: checkCmd('python --version') },
      git: { installed: Boolean(checkCmd('git --version')), version: checkCmd('git --version') },
      adb: { installed: Boolean(checkCmd('adb version')), version: checkCmd('adb version') },
      docker: { installed: Boolean(checkCmd('docker --version')), version: checkCmd('docker --version') },
    },
    platform: process.platform,
    arch: process.arch,
    uptime: Math.round(process.uptime()),
    timestamp: new Date().toISOString()
  };

  res.json(report);
});

// ── 15. Android Device Inspection ───────────────────────────────────────────
router.get('/android/devices', (req, res) => {
  const { execSync } = require('child_process');
  try {
    const raw = execSync('adb devices -l', { timeout: 4000 }).toString();
    const lines = raw.trim().split('\n').slice(1);
    const devices = [];
    for (const line of lines) {
      if (!line.trim()) continue;
      const parts = line.trim().split(/\s+/);
      devices.push({ serial: parts[0], state: parts[1] || 'device' });
    }
    res.json({ available: true, devices });
  } catch (err) {
    res.json({ available: false, error: err.message, devices: [] });
  }
});

// Capture Android screenshot
router.post('/android/screenshot', (req, res) => {
  const { execSync } = require('child_process');
  const path = require('path');
  const fs = require('fs');
  const { projectId, serial } = req.body;
  if (!projectId) return res.status(400).json({ error: 'projectId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  try {
    const snapshotsDir = path.join(project.path, '.snapshots');
    if (!fs.existsSync(snapshotsDir)) fs.mkdirSync(snapshotsDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `android_${serial ? serial.replace(/[^a-zA-Z0-9_-]/g, '') : 'device'}_${timestamp}.png`;
    const targetPath = path.join(snapshotsDir, filename);

    const serialFlag = serial ? `-s ${serial}` : '';
    execSync(`adb ${serialFlag} exec-out screencap -p > "${targetPath}"`, { timeout: 8000 });

    res.json({
      success: true,
      filename,
      url: `/api/snapshots/${projectId}/${filename}/preview`
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── 16. Visual QA & Snapshots ───────────────────────────────────────────────
router.get('/snapshots/:projectId', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  const project = projectService.getProject(req.params.projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const snapshotsDir = path.join(project.path, '.snapshots');
  if (!fs.existsSync(snapshotsDir)) return res.json({ snapshots: [] });

  try {
    const files = fs.readdirSync(snapshotsDir)
      .filter(f => f.endsWith('.png') || f.endsWith('.jpg'))
      .map(filename => {
        const fullPath = path.join(snapshotsDir, filename);
        const stats = fs.statSync(fullPath);
        return {
          filename,
          size: stats.size,
          mtime: stats.mtime,
          url: `/api/snapshots/${req.params.projectId}/${encodeURIComponent(filename)}/preview`
        };
      })
      .sort((a, b) => new Date(b.mtime) - new Date(a.mtime));

    res.json({ snapshots: files });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/snapshots/:projectId/:filename/preview', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  const { projectId, filename } = req.params;
  const cleanFilename = path.basename(filename);
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const targetPath = path.join(project.path, '.snapshots', cleanFilename);
  if (!fs.existsSync(targetPath)) return res.status(404).json({ error: 'Snapshot not found' });

  res.sendFile(targetPath);
});

router.post('/qa/inspect', async (req, res) => {
  const path = require('path');
  const fs = require('fs');
  const { exec } = require('child_process');
  const { projectId, url } = req.body;
  if (!projectId) return res.status(400).json({ error: 'projectId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const targetUrl = url || 'http://localhost:5174';
  const rootDir = path.resolve(__dirname, '../../..');
  const agentDir = path.join(rootDir, 'agent');

  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (fs.existsSync(venvWin)) pythonBin = venvWin;

  const { execFile } = require('child_process');
  const cliScript = path.join(agentDir, 'core', 'agent_cli.py');

  execFile(pythonBin, [cliScript, 'visual-qa', project.path, targetUrl], { timeout: 35000 }, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    try {
      const parsed = JSON.parse(stdout.trim());
      res.json({ success: true, report: parsed });
    } catch {
      res.json({ success: true, raw: stdout });
    }
  });
});

// ── 17. Automated Test Scaffolding ──────────────────────────────────────────
router.post('/tests/scaffold', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  const { projectId } = req.body;
  if (!projectId) return res.status(400).json({ error: 'projectId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  try {
    const pkgPath = path.join(project.path, 'package.json');
    if (fs.existsSync(pkgPath)) {
      // Node / React / Vite project
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      if (!pkg.scripts) pkg.scripts = {};
      pkg.scripts.test = 'vitest run';
      fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2), 'utf8');

      // Create tests directory & smoke test
      const testsDir = path.join(project.path, 'tests');
      if (!fs.existsSync(testsDir)) fs.mkdirSync(testsDir, { recursive: true });

      const testFile = path.join(testsDir, 'smoke.test.jsx');
      if (!fs.existsSync(testFile)) {
        const testCode = `import { describe, it, expect } from 'vitest';

describe('Smoke Test Suite', () => {
  it('verifies test environment sanity', () => {
    expect(true).toBe(true);
  });

  it('validates fundamental logic sanity', () => {
    const sum = (a, b) => a + b;
    expect(sum(2, 3)).toBe(5);
  });
});
`;
        fs.writeFileSync(testFile, testCode, 'utf8');
      }

      // Check vitest.config
      const vitestConfigTs = path.join(project.path, 'vitest.config.ts');
      const vitestConfigJs = path.join(project.path, 'vitest.config.js');
      if (!fs.existsSync(vitestConfigTs) && !fs.existsSync(vitestConfigJs)) {
        const configCode = `import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
  },
});
`;
        fs.writeFileSync(vitestConfigJs, configCode, 'utf8');
      }

      return res.json({
        success: true,
        type: 'node',
        message: 'Vitest automated test suite scaffolded successfully!',
        testCommand: 'npm test'
      });
    }

    // Check Python project
    const pyTestsDir = path.join(project.path, 'tests');
    if (!fs.existsSync(pyTestsDir)) fs.mkdirSync(pyTestsDir, { recursive: true });
    const pyTestFile = path.join(pyTestsDir, 'test_smoke.py');
    if (!fs.existsSync(pyTestFile)) {
      const pyCode = `def test_smoke():
    """Basic smoke test verifying test runner functionality."""
    assert True

def test_math_sanity():
    assert 2 + 2 == 4
`;
      fs.writeFileSync(pyTestFile, pyCode, 'utf8');
    }

    res.json({
      success: true,
      type: 'python',
      message: 'Pytest automated test suite scaffolded successfully!',
      testCommand: 'pytest'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── 18. Project Templates (Section 65) ──────────────────────────────────────
router.get('/templates', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  try {
    const jsonPath = path.resolve(__dirname, '../../../agent/core/project_templates.json');
    if (fs.existsSync(jsonPath)) {
      const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
      return res.json(data);
    }
  } catch (e) {
    console.warn('Failed reading project_templates.json:', e.message);
  }
  res.json([]);
});

router.post('/templates/instantiate', (req, res) => {
  const { templateId, projectName } = req.body;
  const path = require('path');
  const fs = require('fs');

  try {
    const jsonPath = path.resolve(__dirname, '../../../agent/core/project_templates.json');
    const templates = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    const template = templates.find(t => t.id === templateId);
    if (!template) return res.status(404).json({ error: 'Template not found' });

    const cleanName = (projectName || template.title).toLowerCase().replace(/[^a-z0-9_-]/g, '_');
    const project = projectService.createProject(cleanName, template.prompt);

    res.json({ success: true, project, template });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── 19. Checkpoints & Rollback (Sections 50 & 51) ─────────────────────────────
router.get('/checkpoints/:projectId', (req, res) => {
  const project = projectService.getProject(req.params.projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const path = require('path');
  const { execFile } = require('child_process');
  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');

  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  execFile(pythonBin, [cliScript, 'list-checkpoints', project.path], { timeout: 10000 }, (err, stdout) => {
    if (err) return res.json({ checkpoints: [] });
    try {
      res.json({ checkpoints: JSON.parse(stdout.trim()) });
    } catch {
      res.json({ checkpoints: [] });
    }
  });
});

router.post('/checkpoints/create', (req, res) => {
  const { projectId, description, stage } = req.body;
  if (!projectId) return res.status(400).json({ error: 'projectId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const path = require('path');
  const { execFile } = require('child_process');
  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');

  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  const desc = description || 'Manual checkpoint';
  const stg = stage || 'MANUAL';

  execFile(pythonBin, [cliScript, 'create-checkpoint', project.path, desc, stg], { timeout: 15000 }, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.message });
    try {
      res.json({ success: true, ...JSON.parse(stdout.trim()) });
    } catch {
      res.json({ success: true, raw: stdout });
    }
  });
});

router.post('/checkpoints/rollback', (req, res) => {
  const { projectId, checkpointId } = req.body;
  if (!projectId || !checkpointId) return res.status(400).json({ error: 'projectId and checkpointId required' });
  const project = projectService.getProject(projectId);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const path = require('path');
  const { execFile } = require('child_process');
  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');

  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  execFile(pythonBin, [cliScript, 'rollback-checkpoint', project.path, checkpointId], { timeout: 20000 }, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.message });
    try {
      res.json(JSON.parse(stdout.trim()));
    } catch {
      res.json({ success: false, raw: stdout });
    }
  });
});

// Project Memory: Get long-term memory chronicle
router.get('/projects/:id/memory', (req, res) => {
  const project = projectService.getProject(req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');
  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  const { execFile } = require('child_process');
  execFile(pythonBin, [cliScript, 'get-memory', project.path], { timeout: 10000 }, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.message });
    try {
      res.json(JSON.parse(stdout.trim()));
    } catch {
      res.json({ error: 'Invalid JSON response from CLI', raw: stdout });
    }
  });
});

// Project Memory: Save profile & preferences
router.post('/projects/:id/memory', (req, res) => {
  const project = projectService.getProject(req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');
  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  const payload = JSON.stringify(req.body || {});
  const { execFile } = require('child_process');
  execFile(pythonBin, [cliScript, 'save-profile', project.path, payload], { timeout: 10000 }, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.message });
    try {
      res.json(JSON.parse(stdout.trim()));
    } catch {
      res.json({ success: true, raw: stdout });
    }
  });
});

// Multi-Part ZIP: Create chunked project archive
router.post('/projects/:id/zip-chunk', (req, res) => {
  const project = projectService.getProject(req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const maxMb = (req.body && req.body.maxChunkMb) ? String(req.body.maxChunkMb) : '38.0';
  const rootDir = path.resolve(__dirname, '../../..');
  const cliScript = path.join(rootDir, 'agent', 'core', 'agent_cli.py');
  let pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const venvWin = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  if (require('fs').existsSync(venvWin)) pythonBin = venvWin;

  const { execFile } = require('child_process');
  execFile(pythonBin, [cliScript, 'zip-chunk', project.path, maxMb], { timeout: 30000 }, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.message });
    try {
      res.json(JSON.parse(stdout.trim()));
    } catch {
      res.json({ error: 'Invalid JSON response from CLI', raw: stdout });
    }
  });
});

module.exports = router;

