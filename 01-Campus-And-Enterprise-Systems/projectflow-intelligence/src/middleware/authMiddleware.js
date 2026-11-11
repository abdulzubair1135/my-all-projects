const jwt = require('jsonwebtoken');
const { store } = require('../supabase');

const JWT_SECRET = process.env.JWT_SECRET || 'projectflow_jwt_secret_production_key_2026';

// Global Active Sessions Store
store.activeSessions = store.activeSessions || {};

function presenceAndAuthMiddleware(req, res, next) {
  try {
    let email = req.headers['x-user-email'];
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const decoded = jwt.decode(token);
      if (decoded && decoded.email) {
        if (!email) email = decoded.email;
        req.user = decoded;
      }
    }
    if (email) {
      const emailKey = email.trim().toLowerCase();
      store.activeSessions[emailKey] = Date.now();
      req.userEmail = emailKey;
    }
  } catch (e) {
    // Non-fatal presence interceptor
  }
  next();
}

module.exports = {
  JWT_SECRET,
  presenceAndAuthMiddleware
};
