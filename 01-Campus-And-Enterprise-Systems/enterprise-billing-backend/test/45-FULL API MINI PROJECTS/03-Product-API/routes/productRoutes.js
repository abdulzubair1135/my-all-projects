import express from 'express';
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from '../controllers/productController.js';
import { validateProduct } from '../validation/productValidation.js';

const router = express.Router();
router.get('/', getProducts);
router.get('/:id', getProduct);
router.post('/', validateProduct, createProduct);
router.put('/:id', validateProduct, updateProduct);
router.delete('/:id', deleteProduct);

export default router;
