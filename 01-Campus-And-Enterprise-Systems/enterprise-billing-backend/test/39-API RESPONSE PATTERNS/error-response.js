/**
 * Standard Error Response Utility Helper
 * ES Module Format
 */

/**
 * Sends a standardized HTTP error response
 * @param {Object} res - Express response object
 * @param {string} message - Descriptive error message
 * @param {number} statusCode - HTTP status code (Default: 500)
 * @param {*} errorDetails - Additional error info or error stack
 */
export const sendError = (res, message = 'An error occurred', statusCode = 500, errorDetails = null) => {
  return res.status(statusCode).json({
    success: false,
    message: message,
    error: errorDetails
  });
};

export default sendError;
