import jwt from 'jsonwebtoken';
import { env } from '../config/env.js';
import pool from '../config/database.js';
import { AppError } from './error.middleware.js';

export const protect = async (req, res, next) => {
  try {
    let token;
    
    // Check Authorization header
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    } 
    // Check cookies as fallback
    else if (req.cookies && req.cookies.accessToken) {
      token = req.cookies.accessToken;
    }

    if (!token) {
      throw new AppError('Authentication credentials were not provided. Please log in.', 401);
    }

    // Verify token
    let decoded;
    try {
      decoded = jwt.verify(token, env.JWT_ACCESS_SECRET);
    } catch (err) {
      if (err.name === 'TokenExpiredError') {
        throw new AppError('Authentication token has expired. Please refresh your token.', 401);
      }
      throw new AppError('Invalid authentication token.', 401);
    }

    // Check if user still exists and get latest status
    const [rows] = await pool.query(
      'SELECT id, uuid, email, full_name, role, status FROM users WHERE id = ?',
      [decoded.id]
    );

    if (rows.length === 0) {
      throw new AppError('The user belonging to this token no longer exists.', 401);
    }

    const user = rows[0];

    // Check if user account is blocked or suspended
    if (user.status === 'blocked') {
      throw new AppError('Your account has been blocked by administrators.', 403);
    }
    if (user.status === 'suspended') {
      throw new AppError('Your account is currently suspended.', 403);
    }
    if (user.status === 'deleted') {
      throw new AppError('Your account has been deleted.', 401);
    }

    // Attach user information to request
    req.user = user;
    next();
  } catch (err) {
    next(err);
  }
};

export const optionalProtect = async (req, res, next) => {
  try {
    let token;
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    } else if (req.cookies && req.cookies.accessToken) {
      token = req.cookies.accessToken;
    }

    if (!token) {
      return next();
    }

    const decoded = jwt.verify(token, env.JWT_ACCESS_SECRET);
    const [rows] = await pool.query(
      'SELECT id, uuid, email, role, status FROM users WHERE id = ?',
      [decoded.id]
    );

    if (rows.length > 0 && rows[0].status === 'active') {
      req.user = rows[0];
    }
    next();
  } catch (err) {
    next(); // Ignore token errors and proceed as guest
  }
};

