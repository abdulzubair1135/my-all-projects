const logger = require('../utils/logger');

function errorHandler(err, req, res, next) {
  logger.error('SERVER_ERROR', `Unhandled request error: ${err.message}`, {
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    error: err.stack
  });

  const statusCode = err.status || err.statusCode || 500;
  res.status(statusCode).json({
    success: false,
    error: statusCode === 500 ? 'Internal Server Error' : err.message
  });
}

function notFoundHandler(req, res) {
  res.status(404).json({
    success: false,
    error: `Endpoint not found: ${req.method} ${req.originalUrl}`
  });
}

module.exports = {
  errorHandler,
  notFoundHandler
};
