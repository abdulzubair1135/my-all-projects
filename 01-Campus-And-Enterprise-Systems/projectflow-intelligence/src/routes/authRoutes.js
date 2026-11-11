const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const notificationController = require('../controllers/notificationController');

// Authentication Endpoints
router.post('/auth/login', authController.login);
router.post('/auth/signup', authController.signup);
router.post('/auth/dev-login', authController.devLogin);
router.post('/auth/forgot-password', authController.forgotPassword);
router.post('/auth/reset-password', authController.resetPassword);

// Current User Profile
router.get('/me', authController.getMe);
router.patch('/me/profile', authController.updateProfile);

// Device Presence & Tokens
router.post('/users/heartbeat', authController.heartbeat);
router.post('/auth/heartbeat', authController.heartbeat);
router.post('/users/fcm-token', notificationController.registerFcmToken);

module.exports = router;
