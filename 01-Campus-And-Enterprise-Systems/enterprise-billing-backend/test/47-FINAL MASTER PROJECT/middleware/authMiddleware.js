import jwt from 'jsonwebtoken';
import { sendError } from '../utils/response.js';

export const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return sendError(res, 'Access denied. Authorization token missing.', null, 401);
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'super_secret_master_jwt_key_2026');
    req.user = decoded;
    next();
  } catch (error) {
    return sendError(res, 'Invalid or expired token.', error.message, 401);
  }
};

export const authorizeRoles = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !req.user.role) {
      return sendError(res, 'Unauthorized access request.', null, 401);
    }
    if (!allowedRoles.includes(req.user.role)) {
      return sendError(res, `Forbidden. Role '${req.user.role}' cannot perform this operation.`, null, 403);
    }
    next();
  };
};
