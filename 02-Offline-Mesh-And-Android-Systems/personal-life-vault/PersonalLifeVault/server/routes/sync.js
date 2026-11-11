const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const config = require('../config/config');
const { authenticateDevice } = require('../middleware/auth');
const { syncTextBatchSchema } = require('../utils/validation');
const { processTextSyncBatch } = require('../services/syncService');
const { processMediaUpload } = require('../services/mediaService');
const { getDatabase } = require('../database/database');
const logger = require('../utils/logger');

// Staging directory for incoming uploads before SHA-256 verification and date partitioning
const stagingDir = path.join(config.storageRoot, '.staging');
if (!fs.existsSync(stagingDir)) {
  fs.mkdirSync(stagingDir, { recursive: true });
}

const upload = multer({
  dest: stagingDir,
  limits: {
    fileSize: 1024 * 1024 * 2048 // 2048MB (2GB) limit for large file uploads
  }
});

/**
 * POST /api/sync/text
 * Accepts batch of notifications, telecom logs, sensor logs.
 */
router.post('/text', authenticateDevice, (req, res) => {
  const parseResult = syncTextBatchSchema.safeParse(req.body);
  if (!parseResult.success) {
    return res.status(400).json({
      success: false,
      error: 'Invalid sync payload',
      details: parseResult.error.errors.map(e => e.message)
    });
  }

  try {
    const summary = processTextSyncBatch(req.device.deviceId, parseResult.data);
    res.status(200).json({
      success: true,
      device_id: req.device.deviceId,
      inserted: {
        notifications: summary.notifications,
        telecom_logs: summary.telecom_logs,
        sensor_logs: summary.sensor_logs
      },
      total_received: summary.total_received
    });
  } catch (error) {
    logger.error('SYNC', `Failed to process text sync batch: ${error.message}`, {
      deviceId: req.device.deviceId,
      error: error.stack
    });
    res.status(500).json({
      success: false,
      error: 'Database transaction error during text sync'
    });
  }
});

/**
 * POST /api/sync/media
 * Accepts multipart media file upload with metadata.
 */
router.post('/media', authenticateDevice, upload.single('file'), async (req, res, next) => {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      error: 'Missing file in multipart form data'
    });
  }

  try {
    const result = await processMediaUpload(req.device.deviceId, req.file, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/sync/status
 * Returns sync counts and device last seen timestamp.
 */
router.get('/status', authenticateDevice, (req, res) => {
  try {
    const db = getDatabase();
    const notifCount = db.prepare('SELECT COUNT(*) as count FROM notifications WHERE device_id = ?').get(req.device.deviceId).count;
    const telecomCount = db.prepare('SELECT COUNT(*) as count FROM telecom_logs WHERE device_id = ?').get(req.device.deviceId).count;
    const sensorCount = db.prepare('SELECT COUNT(*) as count FROM sensor_logs WHERE device_id = ?').get(req.device.deviceId).count;
    const mediaCount = db.prepare('SELECT COUNT(*) as count FROM media_files WHERE device_id = ?').get(req.device.deviceId).count;

    res.json({
      success: true,
      device_id: req.device.deviceId,
      device_name: req.device.deviceName,
      last_seen: req.device.lastSeen,
      vault_totals: {
        notifications: notifCount,
        telecom_logs: telecomCount,
        sensor_logs: sensorCount,
        media_files: mediaCount
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve device sync status'
    });
  }
});

module.exports = router;
