import { env } from '../config/env.js';

export const errorHandler = (err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  
  // Log the detailed error internally
  console.error(`[Error] Code ${statusCode} - ${req.method} ${req.url}:`, err.message);
  if (err.stack && env.NODE_ENV === 'development') {
    console.error(err.stack);
  }

  // Handle specific database errors without leaking schema details
  let userFriendlyMessage = err.message;
  let validationErrors = err.errors || [];

  if (err.code && err.code.startsWith('ER_')) {
    userFriendlyMessage = 'A database integrity error occurred.';
    if (env.NODE_ENV === 'development') {
      userFriendlyMessage = `Database Error: ${err.message}`;
    }
  }

  res.status(statusCode).json({
    success: false,
    message: userFriendlyMessage || 'Internal Server Error',
    errors: validationErrors
  });
};

// Custom operational error helper
export class AppError extends Error {
  constructor(message, statusCode, errors = []) {
    super(message);
    this.statusCode = statusCode;
    this.errors = errors;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}
