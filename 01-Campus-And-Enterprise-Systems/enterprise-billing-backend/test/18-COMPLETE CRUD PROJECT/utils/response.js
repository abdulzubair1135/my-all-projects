/**
 * Standard API Response Utility Helper
 * Har endpoint se response structure uniform and clean bhejne ke liye use hota hai.
 */

// Success Response Helper
export const sendSuccess = (res, message, data = null, statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data
  });
};

// Error Response Helper
export const sendError = (res, message, error = null, statusCode = 400) => {
  return res.status(statusCode).json({
    success: false,
    message,
    error
  });
};
