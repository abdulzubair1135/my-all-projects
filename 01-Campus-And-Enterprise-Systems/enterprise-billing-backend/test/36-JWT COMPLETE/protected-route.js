// protected-route.js
// Express Router demonstrating JWT protected endpoints

import express from 'express';
import { authenticateToken } from './auth-middleware.js';

const router = express.Router();

// Protected Endpoint 1: User Profile
router.get('/profile', authenticateToken, (req, res) => {
  // req.user was populated by authenticateToken middleware
  res.status(200).json({
    success: true,
    message: "User profile fetched successfully",
    data: {
      user: req.user
    }
  });
});

// Protected Endpoint 2: Admin Dashboard (Role Check)
router.get('/admin/dashboard', authenticateToken, (req, res) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: "Forbidden: Admin privileges required",
      error: "ACCESS_DENIED"
    });
  }

  res.status(200).json({
    success: true,
    message: "Welcome to Admin Dashboard",
    data: {
      secretStats: "Total Revenue: ₹5,00,000"
    }
  });
});

export default router;
