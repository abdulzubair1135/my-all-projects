const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({
      success: false,
      message: 'Access token required',
      code: 'UNAUTHORIZED'
    });
  }

  const jwtSecret = process.env.JWT_SECRET || 'fallback_secret_key';

  jwt.verify(token, jwtSecret, (err, user) => {
    if (err) {
      return res.status(403).json({
        success: false,
        message: 'Invalid or expired token',
        code: 'FORBIDDEN'
      });
    }
    req.user = user;
    next();
  });
};

module.exports = authenticateToken;
