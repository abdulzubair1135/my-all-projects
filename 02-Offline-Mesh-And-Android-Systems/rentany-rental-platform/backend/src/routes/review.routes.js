import { Router } from 'express';
import { body } from 'express-validator';
import { reviewController } from '../controllers/review.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { validateRequest } from '../middleware/validation.middleware.js';

const router = Router();

router.get('/:listingId', reviewController.getListingReviews);

router.post(
  '/',
  protect,
  [
    body('bookingId').isInt().withMessage('Valid booking ID is required.'),
    body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be an integer between 1 and 5.'),
    body('title').optional().trim(),
    body('comment').optional().trim()
  ],
  validateRequest,
  reviewController.createReview
);

export default router;
