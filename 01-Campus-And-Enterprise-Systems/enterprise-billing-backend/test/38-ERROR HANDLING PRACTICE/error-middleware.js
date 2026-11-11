/**
 * Centralized Express Error Handling Middleware
 * ES Module Format
 */

export const errorHandler = (err, req, res, next) => {
  // Default values for error status and message
  let statusCode = err.statusCode || 500;
  let message = err.message || 'Internal Server Error';
  let errorDetails = err.error || null;

  console.error(`[ERROR LOG] ${new Date().toISOString()} - ${req.method} ${req.originalUrl}:`, err);

  // 1. MySQL Duplicate Entry Error (ER_DUP_ENTRY) -> 409 Conflict
  if (err.code === 'ER_DUP_ENTRY') {
    statusCode = 409;
    message = 'Duplicate database record entry detected';
    errorDetails = err.sqlMessage || 'Record already exists';
  }

  // 2. MySQL Foreign Key Constraint Error (ER_ROW_IS_REFERENCED_2) -> 400 Bad Request
  if (err.code === 'ER_ROW_IS_REFERENCED_2' || err.code === 'ER_NO_REFERENCED_ROW_2') {
    statusCode = 400;
    message = 'Foreign key constraint restriction failed';
    errorDetails = 'Referenced relational record does not exist or is constrained';
  }

  // 3. JWT Invalid Token Error -> 401 Unauthorized
  if (err.name === 'JsonWebTokenError') {
    statusCode = 401;
    message = 'Invalid authentication token provided';
  }

  // 4. JWT Token Expired Error -> 401 Unauthorized
  if (err.name === 'TokenExpiredError') {
    statusCode = 401;
    message = 'Authentication token has expired. Please log in again.';
  }

  // 5. Multer File Limit Error -> 400 Bad Request
  if (err.code === 'LIMIT_FILE_SIZE') {
    statusCode = 400;
    message = 'Uploaded file exceeds the maximum allowed size limit';
  }

  // Standard API Error Response
  return res.status(statusCode).json({
    success: false,
    message: message,
    error: errorDetails,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

export default errorHandler;
