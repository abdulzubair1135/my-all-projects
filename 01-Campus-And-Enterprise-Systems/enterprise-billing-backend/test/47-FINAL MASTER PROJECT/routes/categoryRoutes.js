import express from 'express';
import { getCategories, getCategory, createCategory, updateCategory, deleteCategory } from '../controllers/categoryController.js';
import { verifyToken, authorizeRoles } from '../middleware/authMiddleware.js';

const router = express.Router();

router.get('/', getCategories);
router.get('/:id', getCategory);

// Protected Admin Routes
router.post('/', verifyToken, authorizeRoles('admin'), createCategory);
router.put('/:id', verifyToken, authorizeRoles('admin'), updateCategory);
router.delete('/:id', verifyToken, authorizeRoles('admin'), deleteCategory);

export default router;
