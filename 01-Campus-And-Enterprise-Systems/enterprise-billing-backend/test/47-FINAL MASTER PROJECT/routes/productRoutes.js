import express from 'express';
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from '../controllers/productController.js';
import { validateProduct } from '../validation/productValidation.js';
import { verifyToken, authorizeRoles } from '../middleware/authMiddleware.js';
import { upload } from '../middleware/uploadMiddleware.js';

const router = express.Router();

router.get('/', getProducts);
router.get('/:id', getProduct);

// Protected Admin Routes
router.post('/', verifyToken, authorizeRoles('admin'), upload.single('image'), validateProduct, createProduct);
router.put('/:id', verifyToken, authorizeRoles('admin'), upload.single('image'), validateProduct, updateProduct);
router.delete('/:id', verifyToken, authorizeRoles('admin'), deleteProduct);

export default router;
