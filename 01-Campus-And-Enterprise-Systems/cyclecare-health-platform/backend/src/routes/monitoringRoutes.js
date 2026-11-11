const express = require('express');
const router = express.Router();
const monitoringController = require('../controllers/monitoringController');
const authenticateToken = require('../middleware/auth');

// Optional auth wrapper: attaches req.user if a valid token is present, but doesn't reject if not
const optionalAuth = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return next();
  authenticateToken(req, res, () => next());
};

// Error ingestion (accessible from Android client, web client, or backend)
router.post('/errors', optionalAuth, monitoringController.reportError);

// FCM Device Token Registration
router.post('/register-token', authenticateToken, monitoringController.registerDeviceToken);

module.exports = router;
