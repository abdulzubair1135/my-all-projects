import { Router } from 'express';
import { body } from 'express-validator';
import { userController } from '../controllers/user.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { validateRequest } from '../middleware/validation.middleware.js';
import { upload } from '../middleware/upload.middleware.js';

const router = Router();

router.get('/me', protect, userController.getProfile);
router.put(
  '/me',
  protect,
  [
    body('full_name').optional().notEmpty().withMessage('Full name cannot be empty.'),
    body('email').optional().isEmail().withMessage('Invalid email format.'),
    body('phone').optional().notEmpty().withMessage('Phone cannot be empty.')
  ],
  validateRequest,
  userController.updateProfile
);

router.post(
  '/me/profile-image',
  protect,
  upload.single('image'),
  userController.uploadProfileImage
);

router.get('/:id/public', userController.getPublicProfile);

// Relationships
router.get('/me/listings', protect, userController.getMyListings);
router.get('/me/bookings', protect, userController.getMyBookings);
router.get('/me/reviews', protect, userController.getMyReviews);
router.get('/me/wishlist', protect, userController.getMyWishlist);
router.delete('/me', protect, userController.deleteProfile);

// Addresses sub-resource
router.get('/me/addresses', protect, userController.getAddresses);
router.post(
  '/me/addresses',
  protect,
  [
    body('address_line').notEmpty().withMessage('Address line is required.'),
    body('city').notEmpty().withMessage('City is required.'),
    body('state').notEmpty().withMessage('State is required.'),
    body('country').notEmpty().withMessage('Country is required.'),
    body('postal_code').notEmpty().withMessage('Postal code is required.'),
    body('latitude').isNumeric().withMessage('Latitude must be a number.'),
    body('longitude').isNumeric().withMessage('Longitude must be a number.')
  ],
  validateRequest,
  userController.addAddress
);

router.delete('/me/addresses/:id', protect, userController.deleteAddress);
router.patch('/me/addresses/:id/default', protect, userController.setDefaultAddress);

export default router;
