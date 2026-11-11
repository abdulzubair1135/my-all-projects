const express = require('express');
const router = express.Router();
const crypto = require('crypto');
const config = require('../config/config');
const { getDatabase } = require('../database/database');
const { registerDeviceSchema } = require('../utils/validation');
const { authenticateDevice, hashToken } = require('../middleware/auth');
const logger = require('../utils/logger');

router.post('/register', (req, res) => {
  const parseResult = registerDeviceSchema.safeParse(req.body);
  if (!parseResult.success) {
    return res.status(400).json({
      success: false,
      error: 'Invalid registration parameters',
      details: parseResult.error.errors.map(e => e.message)
    });
  }

  const { device_id, device_name, admin_key } = parseResult.data;

  // Constant-time comparison to prevent timing attacks
  const expectedKey = Buffer.from(config.adminRegistrationKey);
  const providedKey = Buffer.from(admin_key);

  if (expectedKey.length !== providedKey.length || !crypto.timingSafeEqual(expectedKey, providedKey)) {
    logger.warn('DEVICE', 'Device registration failed: Invalid master registration key', {
      device_id,
      ip: req.ip
    });
    return res.status(403).json({
      success: false,
      error: 'Forbidden: Invalid admin registration key'
    });
  }

  // Generate a cryptographically secure 256-bit authentication token
  const rawToken = crypto.randomBytes(32).toString('hex');
  const tokenHash = hashToken(rawToken);
  const now = Date.now();

  try {
    const db = getDatabase();
    
    // Check if device already exists
    const existing = db.prepare('SELECT id, auth_token_hash FROM devices WHERE device_id = ?').get(device_id);

    let returnToken = rawToken;

    if (existing && existing.auth_token_hash && req.body.force_reset_token !== true) {
      // Preserve existing token hash so concurrent registration calls don't invalidate active sessions
      db.prepare(`
        UPDATE devices 
        SET device_name = CASE WHEN device_name IS NULL OR device_name = '' OR device_name = 'Phone' OR device_name = 'Unnamed Device' THEN ? ELSE device_name END,
            last_seen = ?
        WHERE device_id = ?
      `).run(device_name, now, device_id);

      logger.info('DEVICE', `Device last_seen updated for existing device: ${device_id}`);
      returnToken = null; // Client already has valid token stored
    } else if (existing) {
      db.prepare(`
        UPDATE devices 
        SET device_name = CASE WHEN device_name IS NULL OR device_name = '' OR device_name = 'Phone' OR device_name = 'Unnamed Device' THEN ? ELSE device_name END,
            auth_token_hash = ?, 
            last_seen = ?
        WHERE device_id = ?
      `).run(device_name, tokenHash, now, device_id);

      logger.info('DEVICE', `Device token updated for existing device: ${device_id}`);
    } else {
      db.prepare(`
        INSERT INTO devices (device_id, device_name, auth_token_hash, created_at, last_seen)
        VALUES (?, ?, ?, ?, ?)
      `).run(device_id, device_name, tokenHash, now, now);

      logger.info('DEVICE', `New device successfully registered: ${device_id}`);
    }

    return res.status(200).json({
      success: true,
      message: 'Device successfully registered to Personal Life Vault',
      device_id,
      token: returnToken
    });
  } catch (error) {
    logger.error('DEVICE', `Database error during device registration: ${error.message}`, {
      deviceId: device_id,
      error: error.stack
    });
    return res.status(500).json({
      success: false,
      error: 'Database error registering device'
    });
  }
});

/**
 * POST /api/device/command (Called by Web Dashboard)
 * Enqueues a remote command for an online Android device (e.g. EXPLORE_DIR, BACKUP_FILE)
 */
router.post('/command', (req, res) => {
  const { device_id, command_type, payload } = req.body;
  if (!device_id || !command_type) {
    return res.status(400).json({ success: false, error: 'device_id and command_type are required' });
  }

  try {
    const db = getDatabase();
    const now = Date.now();
    const payloadStr = typeof payload === 'object' ? JSON.stringify(payload) : (payload || '{}');

    const result = db.prepare(`
      INSERT INTO device_commands (device_id, command_type, payload, status, created_at, updated_at)
      VALUES (?, ?, ?, 'PENDING', ?, ?)
    `).run(device_id, command_type, payloadStr, now, now);

    logger.info('DEVICE_CMD', `Enqueued remote command ${command_type} (id=${result.lastInsertRowid}) for device ${device_id}`);

    res.json({
      success: true,
      command_id: result.lastInsertRowid,
      device_id,
      command_type,
      status: 'PENDING'
    });
  } catch (error) {
    logger.error('DEVICE_CMD', `Error enqueuing command: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/device/poll-commands (Called by Android App)
 * Returns pending commands assigned to this authenticated device.
 */
router.post('/poll-commands', authenticateDevice, (req, res) => {
  try {
    const db = getDatabase();
    const deviceId = req.device.deviceId;

    const pending = db.prepare(`
      SELECT id, command_type, payload, created_at
      FROM device_commands
      WHERE device_id = ? AND status = 'PENDING'
      ORDER BY id ASC
    `).all(deviceId);

    // Update status of fetched commands to 'PROCESSING'
    if (pending.length > 0) {
      const now = Date.now();
      const ids = pending.map(c => c.id);
      db.prepare(`
        UPDATE device_commands
        SET status = 'PROCESSING', updated_at = ?
        WHERE id IN (${ids.join(',')})
      `).run(now);
    }

    res.json({
      success: true,
      commands: pending.map(c => ({
        id: c.id,
        command_type: c.command_type,
        payload: JSON.parse(c.payload || '{}'),
        created_at: c.created_at
      }))
    });
  } catch (error) {
    logger.error('DEVICE_CMD', `Error polling commands: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * POST /api/device/command-result (Called by Android App)
 * Reports the status and result data of an executed remote command.
 */
router.post('/command-result', authenticateDevice, (req, res) => {
  const { command_id, status, result } = req.body;
  if (!command_id || !status) {
    return res.status(400).json({ success: false, error: 'command_id and status are required' });
  }

  try {
    const db = getDatabase();
    const now = Date.now();
    const resultStr = typeof result === 'object' ? JSON.stringify(result) : (result || '{}');

    db.prepare(`
      UPDATE device_commands
      SET status = ?, result = ?, updated_at = ?
      WHERE id = ? AND device_id = ?
    `).run(status, resultStr, now, command_id, req.device.deviceId);

    logger.info('DEVICE_CMD', `Command ${command_id} updated status to ${status} for device ${req.device.deviceId}`);

    res.json({ success: true, command_id, status });
  } catch (error) {
    logger.error('DEVICE_CMD', `Error updating command result: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/device/command/:id (Called by Web Dashboard)
 * Checks the current status and result payload of a command.
 */
router.get('/command/:id', (req, res) => {
  try {
    const db = getDatabase();
    const cmd = db.prepare(`
      SELECT id, device_id, command_type, payload, status, result, created_at, updated_at
      FROM device_commands
      WHERE id = ?
    `).get(req.params.id);

    if (!cmd) {
      return res.status(404).json({ success: false, error: 'Command not found' });
    }

    res.json({
      success: true,
      command: {
        id: cmd.id,
        device_id: cmd.device_id,
        command_type: cmd.command_type,
        payload: JSON.parse(cmd.payload || '{}'),
        status: cmd.status,
        result: cmd.result ? JSON.parse(cmd.result) : null,
        created_at: cmd.created_at,
        updated_at: cmd.updated_at
      }
    });
  } catch (error) {
    logger.error('DEVICE_CMD', `Error reading command status: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

// In-memory progress store (session_id -> progress data)
const uploadProgressStore = new Map();

// POST /api/device/upload-progress — Android reports MB-by-MB progress
router.post('/upload-progress', (req, res) => {
  try {
    const { session_id, uploaded_bytes, total_bytes, file_name, percent } = req.body;
    if (!session_id) return res.json({ success: false });
    uploadProgressStore.set(session_id, {
      session_id, file_name,
      uploaded_bytes: parseInt(uploaded_bytes) || 0,
      total_bytes: parseInt(total_bytes) || 0,
      percent: parseInt(percent) || 0,
      updated_at: Date.now()
    });
    const cutoff = Date.now() - 7200000;
    for (const [k, v] of uploadProgressStore.entries()) {
      if (v.updated_at < cutoff) uploadProgressStore.delete(k);
    }
    res.json({ success: true });
  } catch (e) { res.json({ success: false, error: e.message }); }
});

// GET /api/device/upload-progress/:sessionId — Dashboard polls for progress
router.get('/upload-progress/:sessionId', (req, res) => {
  const data = uploadProgressStore.get(req.params.sessionId);
  res.json({ success: true, progress: data || null });
});

// GET /api/device/upload-progress-all — All active upload sessions
router.get('/upload-progress-all', (req, res) => {
  const all = Array.from(uploadProgressStore.values())
    .filter(p => Date.now() - p.updated_at < 300000)
    .sort((a, b) => b.updated_at - a.updated_at);
  res.json({ success: true, sessions: all });
});

module.exports = router;

