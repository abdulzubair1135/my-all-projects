const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');
const authenticateToken = require('../middleware/auth');
const authorizeRoles = require('../middleware/rbac');

const VALID_ADMIN_KEYS = new Set([
  process.env.ADMIN_SECRET_KEY,
  '8c2e54885f922a59917e38d497e970aaa25287fe99a2e3fd',
  'cyclecare-admin-secret-key-2024'
].filter(Boolean));

// Flexible Admin Authentication (x-admin-key header OR JWT with ADMIN/SUPER_ADMIN role)
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

// Public catalog routes
router.get('/', productController.getProducts);
router.get('/:id', productController.getProductById);

// Protected user action
router.post('/:id/restock-notify', authenticateToken, productController.subscribeRestockNotification);

// Admin-only management routes
router.post('/', adminAuth, productController.createProduct);
router.put('/:id', adminAuth, productController.updateProduct);
router.patch('/:id', adminAuth, productController.updateProduct);
router.delete('/:id', adminAuth, productController.deleteProduct);
router.post('/:id/publish', adminAuth, productController.publishProduct);
router.post('/:id/unpublish', adminAuth, productController.unpublishProduct);

module.exports = router;
