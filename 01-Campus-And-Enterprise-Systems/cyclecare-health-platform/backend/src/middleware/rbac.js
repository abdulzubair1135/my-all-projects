const authorizeRoles = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'Permission denied: Insufficient role privileges',
        code: 'ROLE_FORBIDDEN'
      });
    }
    next();
  };
};

module.exports = authorizeRoles;
