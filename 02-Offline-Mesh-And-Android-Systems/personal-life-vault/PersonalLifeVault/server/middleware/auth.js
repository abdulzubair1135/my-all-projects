const crypto = require('crypto');
const { getDatabase } = require('../database/database');
const { recordFailedAttempt } = require('./securityHardening');
const logger = require('../utils/logger');

/**
 * Computes SHA-256 hash of a string.
 * @param {string} text 
 * @returns {string} Hex encoded hash
 */
function hashToken(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

/**
 * Authentication middleware for registered sync devices.
 * Expects 'Authorization: Bearer <token>'
 */
function authenticateDevice(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    recordFailedAttempt(req.ip);
    logger.warn('AUTH', 'Authentication failed: Missing or malformed Authorization header', {
      ip: req.ip,
      path: req.originalUrl
    });
    return res.status(401).json({
      success: false,
      error: 'Unauthorized: Missing or invalid Bearer token'
    });
  }

  const rawToken = authHeader.substring(7).trim();
  if (!rawToken) {
    recordFailedAttempt(req.ip);
    return res.status(401).json({
      success: false,
      error: 'Unauthorized: Empty token provided'
    });
  }

  const tokenHash = hashToken(rawToken);

  try {
    const db = getDatabase();
    const query = db.prepare('SELECT id, device_id, device_name, created_at, last_seen FROM devices WHERE auth_token_hash = ?');
    const device = query.get(tokenHash);

    if (!device) {
      recordFailedAttempt(req.ip);
      logger.warn('AUTH', 'Authentication failed: Token hash not found', {
        ip: req.ip,
        path: req.originalUrl
      });
      return res.status(401).json({
        success: false,
        error: 'Unauthorized: Device not recognized or invalid token'
      });
    }

    // Update last_seen asynchronously in DB
    const now = Date.now();
    db.prepare('UPDATE devices SET last_seen = ? WHERE id = ?').run(now, device.id);

    // Attach verified device info to request
    req.device = {
      id: device.id,
      deviceId: device.device_id,
      deviceName: device.device_name,
      lastSeen: now
    };

    next();
  } catch (err) {
    logger.error('AUTH', `Authentication verification error: ${err.message}`, { error: err.stack });
    return res.status(500).json({
      success: false,
      error: 'Internal server error during authentication'
    });
  }
}

module.exports = {
  authenticateDevice,
  hashToken
};
