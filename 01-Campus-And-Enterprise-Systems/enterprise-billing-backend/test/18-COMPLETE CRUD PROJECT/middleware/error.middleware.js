/**
 * Global Error Handler Middleware
 * Express me unhandled runtime exceptions catch karta hai.
 */

import { sendError } from '../utils/response.js';

export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Global Server Error:', err.stack || err.message);

  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  return sendError(res, message, process.env.NODE_ENV === 'development' ? err.stack : null, statusCode);
};
