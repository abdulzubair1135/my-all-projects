import express from 'express';
import { checkout, getMyOrders, getOrderDetails } from '../controllers/orderController.js';
import { validateOrder } from '../validation/orderValidation.js';
import { verifyToken } from '../middleware/authMiddleware.js';

const router = express.Router();

// All Order routes require authentication
router.use(verifyToken);

router.post('/checkout', validateOrder, checkout);
router.get('/my-orders', getMyOrders);
router.get('/:id', getOrderDetails);

export default router;
