import { sendError } from '../utils/response.js';

export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Global Error Handler Caught:', err);

  let statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  let message = err.message || 'Internal Server Error';

  // MySQL Duplicate Key Error
  if (err.code === 'ER_DUP_ENTRY') {
    statusCode = 400;
    message = 'Duplicate entry error: Record already exists.';
  }

  // Multer Error Handling
  if (err.name === 'MulterError') {
    statusCode = 400;
    message = `File upload error: ${err.message}`;
  }

  return sendError(res, message, process.env.NODE_ENV === 'development' ? err.stack : undefined, statusCode);
};
