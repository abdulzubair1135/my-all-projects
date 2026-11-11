/**
 * Public Unauthenticated Routes Module
 * ES Module Format
 */

import express from 'express';

const router = express.Router();

/**
 * Server Health Check Endpoint
 * GET /api/public/health
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'API server is running healthy',
    timestamp: new Date().toISOString()
  });
});

/**
 * Public User Login Endpoint
 * POST /api/public/login
 */
router.post('/login', (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({
      success: false,
      message: 'Email and password are required'
    });
  }

  res.status(200).json({
    success: true,
    message: 'User authenticated successfully',
    data: {
      token: 'mock-jwt-token-string',
      user: { email, role: 'student' }
    }
  });
});

/**
 * Public User Registration Endpoint
 * POST /api/public/register
 */
router.post('/register', (req, res) => {
  const { name, email, password } = req.body;

  res.status(201).json({
    success: true,
    message: 'Account created successfully',
    data: { name, email }
  });
});

export default router;
