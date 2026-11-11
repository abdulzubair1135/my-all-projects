const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const itemController = require('../controllers/itemController');
const billController = require('../controllers/billController');

// Authentication Middleware
const isAuthenticated = (req, res, next) => {
    if (req.session.userId) {
        return next();
    }
    res.redirect('/login.html');
};

// Auth Routes
router.post('/api/login', authController.login);
router.get('/api/logout', authController.logout);
router.get('/api/user-session', authController.getSessionUser);

// Protected API Routes
router.get('/api/items', isAuthenticated, itemController.getItems);
router.post('/api/generate-bill', isAuthenticated, billController.createBill);
router.get('/api/bill/:id', isAuthenticated, billController.getBillDetails);

module.exports = router;
