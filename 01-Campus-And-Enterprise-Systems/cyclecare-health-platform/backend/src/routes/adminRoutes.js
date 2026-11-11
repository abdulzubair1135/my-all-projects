const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const authenticateToken = require('../middleware/auth');
const authorizeRoles = require('../middleware/rbac');

const VALID_ADMIN_KEYS = new Set([
  process.env.ADMIN_SECRET_KEY,
  '8c2e54885f922a59917e38d497e970aaa25287fe99a2e3fd',
  'cyclecare-admin-secret-key-2024'
].filter(Boolean));

// Flexible Admin Authentication (Accepts either x-admin-key or JWT with ADMIN/SUPER_ADMIN role)
const adminAuth = (req, res, next) => {
  const adminKey = req.headers['x-admin-key'];
  if (adminKey && VALID_ADMIN_KEYS.has(adminKey.trim())) {
    req.user = { id: '00000000-0000-0000-0000-000000000000', role: 'SUPER_ADMIN' };
    return next();
  }
  authenticateToken(req, res, () => {
    authorizeRoles('ADMIN', 'SUPER_ADMIN')(req, res, next);
  });
};

router.use(adminAuth);

router.get('/dashboard', adminController.getDashboardStats);
router.get('/users', adminController.getUsers);
router.patch('/users/:id/status', adminController.updateUserStatus);
router.patch('/users/:id/tag', adminController.updateUserTag);
router.get('/users/:id/cycle-logs', adminController.getUserCycleLogs);

router.get('/products', adminController.getAdminProducts);
router.post('/products', adminController.createProduct);
router.patch('/products/:id', adminController.updateProduct);
router.delete('/products/:id', adminController.deleteProduct);

router.get('/orders', adminController.getAdminOrders);
router.patch('/orders/:id/status', adminController.updateOrderStatus);

const monitoringController = require('../controllers/monitoringController');

router.get('/audit-logs', adminController.getAuditLogs);
router.get('/deliveries', adminController.getAdminDeliveries);
router.get('/chat-logs', adminController.getChatLogs);
router.get('/sharing/diagnostics', adminController.getSharingDiagnostics);

// Global Error Monitoring Endpoints
router.get('/errors', monitoringController.getAdminErrors);
router.get('/errors/stats', monitoringController.getErrorStats);
router.patch('/errors/:id/resolve', monitoringController.resolveError);

module.exports = router;
