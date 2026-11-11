// auth-middleware.js
// Production & Exam ready Express Authentication Middleware using JWT

import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
dotenv.config();

export const authenticateToken = (req, res, next) => {
  try {
    // 1. Fetch Authorization header
    const authHeader = req.headers['authorization'];

    // 2. Check if header exists and follows Bearer schema
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: "Access denied. Authentication token missing.",
        error: "NO_TOKEN"
      });
    }

    // 3. Extract actual token string
    const token = authHeader.split(' ')[1];

    // 4. Verify token using secret key
    const secretKey = process.env.JWT_SECRET || 'fallback_exam_secret';
    const decoded = jwt.verify(token, secretKey);

    // 5. Attach decoded payload to request object for downstream controllers
    req.user = decoded;

    // 6. Pass execution control to next handler
    next();

  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: "Session expired. Please log in again.",
        error: "TOKEN_EXPIRED"
      });
    }

    return res.status(403).json({
      success: false,
      message: "Invalid or tampered token.",
      error: "INVALID_TOKEN"
    });
  }
};
