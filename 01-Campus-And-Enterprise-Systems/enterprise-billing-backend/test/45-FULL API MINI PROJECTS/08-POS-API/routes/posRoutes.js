import express from 'express';
import { checkoutOrder, getOrders, getOrder } from '../controllers/posController.js';
import { validateOrder } from '../validation/posValidation.js';

const router = express.Router();
router.post('/checkout', validateOrder, checkoutOrder);
router.get('/orders', getOrders);
router.get('/orders/:id', getOrder);

export default router;
