const express = require('express');
const router = express.Router();
const paymentsController = require('../controllers/paymentsController');
const authenticateToken = require('../middleware/auth');

router.post('/create', authenticateToken, paymentsController.createPaymentOrder);
router.post('/verify', authenticateToken, paymentsController.verifyPayment);
router.post('/webhook', paymentsController.handleWebhook);

router.post('/demo/create', authenticateToken, paymentsController.createDemoPayment);
router.post('/demo/success', authenticateToken, paymentsController.handleDemoPaymentSuccess);
router.post('/demo/fail', authenticateToken, paymentsController.handleDemoPaymentFail);
router.post('/demo/cancel', authenticateToken, paymentsController.handleDemoPaymentCancel);

module.exports = router;
