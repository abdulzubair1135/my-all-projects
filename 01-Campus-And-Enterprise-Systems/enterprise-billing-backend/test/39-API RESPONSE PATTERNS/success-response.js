/**
 * Standard Success Response Utility Helper
 * ES Module Format
 */

/**
 * Sends a standardized HTTP success response
 * @param {Object} res - Express response object
 * @param {*} data - Response payload data (Object, Array, null)
 * @param {string} message - Human readable message
 * @param {number} statusCode - HTTP status code (Default: 200)
 */
export const sendSuccess = (res, data = null, message = 'Operation successful', statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    message: message,
    data: data
  });
};

export default sendSuccess;
