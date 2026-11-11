const express = require('express');
const router = express.Router();
const fs = require('fs');
const { getDatabase } = require('../database/database');
const config = require('../config/config');

router.get('/', (req, res) => {
  let dbStatus = 'healthy';
  let deviceCount = 0;

  try {
    const db = getDatabase();
    const result = db.prepare('SELECT COUNT(*) as count FROM devices').get();
    deviceCount = result ? result.count : 0;
  } catch (error) {
    dbStatus = `unhealthy: ${error.message}`;
  }

  const vaultAccessible = fs.existsSync(config.storageRoot);

  res.json({
    status: 'ok',
    service: 'Personal Life Vault',
    version: '1.0.0',
    timestamp: Date.now(),
    timezone: config.timezone,
    uptime_seconds: Math.floor(process.uptime()),
    database: {
      status: dbStatus,
      registered_devices: deviceCount
    },
    storage: {
      root: config.storageRoot,
      accessible: vaultAccessible
    }
  });
});

module.exports = router;
