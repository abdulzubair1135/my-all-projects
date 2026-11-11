/**
 * Standard Login Response Utility Helper
 * ES Module Format
 */

/**
 * Sends a standardized HTTP login response with token and sanitized user profile
 * @param {Object} res - Express response object
 * @param {Object} user - User record (password should be excluded/deleted)
 * @param {string} token - JWT authentication token
 * @param {string} message - Success message
 */
export const sendLoginResponse = (
  res,
  user,
  token,
  message = 'User logged in successfully'
) => {
  // Ensure sensitive password hash is excluded from payload
  const { password, ...userProfile } = user;

  return res.status(200).json({
    success: true,
    message: message,
    data: {
      user: userProfile,
      token: token,
      tokenType: 'Bearer'
    }
  });
};

export default sendLoginResponse;
