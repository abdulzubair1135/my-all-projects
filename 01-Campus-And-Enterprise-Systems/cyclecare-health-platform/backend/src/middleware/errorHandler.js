const pool = require('../config/db');

const errorHandler = (err, req, res, next) => {
  console.error('[Error Stack]', err.stack || err);

  const statusCode = res.statusCode !== 200 ? res.statusCode : 500;

  // Asynchronously record 5xx server errors into app_error_logs
  if (statusCode >= 500 || err.status >= 500) {
    try {
      const query = `
        INSERT INTO app_error_logs
          (source, severity, message, stack, route, method, user_id, status_code, metadata)
        VALUES
          ($1, $2, $3, $4, $5, $6, $7, $8, $9);
      `;
      const values = [
        'BACKEND',
        statusCode === 500 ? 'CRITICAL' : 'ERROR',
        err.message || 'Unknown Server Error',
        err.stack || null,
        req.originalUrl || req.url || null,
        req.method || null,
        req.user ? req.user.id : null,
        statusCode,
        JSON.stringify({ query: req.query, ip: req.ip })
      ];
      pool.query(query, values).catch(dbErr => {
        console.error('[Failed to log error to DB]', dbErr.message);
      });
    } catch (e) {
      // Fail silently to ensure response still returns
    }
  }

  res.status(statusCode).json({
    success: false,
    message: err.message || 'Internal Server Error',
    code: err.code || 'SERVER_ERROR'
  });
};

module.exports = errorHandler;
