import { Router } from 'express';
import { body } from 'express-validator';
import { listingController } from '../controllers/listing.controller.js';
import { protect, optionalProtect } from '../middleware/auth.middleware.js';
import { validateRequest } from '../middleware/validation.middleware.js';
import { upload } from '../middleware/upload.middleware.js';

const router = Router();

// Validation rules
const listingValidators = [
  body('title').notEmpty().withMessage('Listing title is required.'),
  body('description').notEmpty().withMessage('Listing description is required.'),
  body('category_id').isInt().withMessage('Valid category ID is required.'),
  body('price_per_day').isNumeric().withMessage('Price per day must be a numeric value.'),
  body('location_address').notEmpty().withMessage('Location address is required.'),
  body('city').notEmpty().withMessage('City is required.'),
  body('state').notEmpty().withMessage('State is required.'),
  body('country').notEmpty().withMessage('Country is required.'),
  body('postal_code').notEmpty().withMessage('Postal code is required.'),
  body('latitude').isNumeric().withMessage('Latitude must be a valid coordinate.'),
  body('longitude').isNumeric().withMessage('Longitude must be a valid coordinate.')
];

// Public Endpoints
router.get('/', listingController.getListings);
router.get('/nearby', listingController.getNearby);
router.get('/:id', optionalProtect, listingController.getListingDetails);

// Protected Endpoints
router.post('/', protect, listingValidators, validateRequest, listingController.createListing);
router.put('/:id', protect, listingController.updateListing); // Allow partial updates without full validators
router.delete('/:id', protect, listingController.deleteListing);

// Image uploading sub-resource
router.post('/:id/images', protect, upload.array('images', 5), listingController.uploadListingImages);
router.delete('/:id/images/:imageId', protect, listingController.deleteListingImage);

// Status toggling
router.patch('/:id/status', protect, listingController.updateListingStatus);

export default router;
