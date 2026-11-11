/**
 * Authentication Routes Definition
 */

import express from 'express';
import { registerController } from '../controllers/register.controller.js';
import { loginController, getProfileController } from '../controllers/login.controller.js';
import { registerValidationRules, loginValidationRules } from '../validation/auth.validation.js';
import { authMiddleware } from '../middleware/auth.middleware.js';

const router = express.Router();

// Base Path: /api/auth

// POST /api/auth/register
router.post('/register', registerValidationRules, registerController);

// POST /api/auth/login
router.post('/login', loginValidationRules, loginController);

// GET /api/auth/me (Protected Route)
router.get('/me', authMiddleware, getProfileController);

export default router;
