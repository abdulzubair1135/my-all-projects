import { Router } from 'express';
import { body } from 'express-validator';
import { authController } from '../controllers/auth.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { validateRequest } from '../middleware/validation.middleware.js';
import { authLimiter } from '../config/security.js';

const router = Router();

router.post(
  '/register',
  authLimiter,
  [
    body('full_name').notEmpty().withMessage('Full name is required.'),
    body('email').isEmail().withMessage('Please provide a valid email address.'),
    body('phone').notEmpty().withMessage('Phone number is required.'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters long.')
  ],
  validateRequest,
  authController.register
);

router.post(
  '/login',
  authLimiter,
  [
    body('email').isEmail().withMessage('Please provide a valid email address.'),
    body('password').notEmpty().withMessage('Password is required.')
  ],
  validateRequest,
  authController.login
);

router.post(
  '/refresh',
  [
    body('refreshToken').notEmpty().withMessage('Refresh token is required.')
  ],
  validateRequest,
  authController.refresh
);

router.post('/logout', authController.logout);

router.get('/me', protect, authController.getMe);

router.post(
  '/forgot-password',
  [
    body('email').isEmail().withMessage('Please provide a valid email address.')
  ],
  validateRequest,
  authController.forgotPassword
);

router.post(
  '/reset-password',
  [
    body('email').isEmail().withMessage('Please provide a valid email address.'),
    body('newPassword').isLength({ min: 6 }).withMessage('New password must be at least 6 characters long.')
  ],
  validateRequest,
  authController.resetPassword
);

export default router;
