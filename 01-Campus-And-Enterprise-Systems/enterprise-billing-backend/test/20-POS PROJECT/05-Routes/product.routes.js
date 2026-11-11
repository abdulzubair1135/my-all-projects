/**
 * Product Routes
 */

import express from 'express';
import { getProducts, getProductById, createProduct } from '../04-Controllers/product.controller.js';
import { productRules } from '../07-Validation/product.validation.js';
import { authMiddleware } from '../06-Middleware/auth.middleware.js';

const router = express.Router();

router.get('/', getProducts);
router.get('/:id', getProductById);
router.post('/', authMiddleware, productRules, createProduct);

export default router;
