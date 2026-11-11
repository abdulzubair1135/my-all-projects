/**
 * Authenticated Protected Routes Module (Requires Valid JWT Token)
 * ES Module Format
 */

import express from 'express';

const router = express.Router();

// Mock JWT Authentication Middleware
const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      success: false,
      message: 'Access denied. Missing or invalid Authorization header token.'
    });
  }
  
  // Attach decoded user info to request
  req.user = { id: 101, name: 'Student User', role: 'student' };
  next();
};

// Mount Authentication Middleware to all routes in this router
router.use(verifyToken);

/**
 * Get Authenticated User Profile
 * GET /api/user/profile
 */
router.get('/profile', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'User profile retrieved successfully',
    data: req.user
  });
});

/**
 * Update User Profile Details
 * PUT /api/user/profile
 */
router.put('/profile', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'User profile updated',
    data: { ...req.user, ...req.body }
  });
});

export default router;
