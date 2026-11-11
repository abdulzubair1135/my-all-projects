import { Router } from 'express';
import { body } from 'express-validator';
import { bookingController } from '../controllers/booking.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { validateRequest } from '../middleware/validation.middleware.js';

const router = Router();

router.post(
  '/',
  protect,
  [
    body('listingId').isInt().withMessage('Valid listing ID is required.'),
    body('startDate').isDate().withMessage('Please select a valid start date.'),
    body('endDate').isDate().withMessage('Please select a valid end date.'),
    body('deliveryType').isIn(['Self Pickup', 'Delivery']).withMessage('Delivery type must be Self Pickup or Delivery.'),
    body('quantity').optional().isInt({ min: 1 }).withMessage('Quantity must be at least 1.')
  ],
  validateRequest,
  bookingController.createBooking
);

router.get('/me', protect, bookingController.getMyBookings);
router.get('/:id', protect, bookingController.getBooking);

router.patch(
  '/:id/cancel',
  protect,
  [
    body('reason').notEmpty().withMessage('Cancellation reason is required.')
  ],
  validateRequest,
  bookingController.cancelBooking
);

router.patch('/:id/confirm', protect, bookingController.confirmBooking);
router.patch('/:id/start', protect, bookingController.startBooking);
router.patch('/:id/return', protect, bookingController.returnBooking);
router.patch('/:id/complete', protect, bookingController.completeBooking);

export default router;
