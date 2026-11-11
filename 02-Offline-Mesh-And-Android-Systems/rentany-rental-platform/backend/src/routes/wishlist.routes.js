import { Router } from 'express';
import { wishlistController } from '../controllers/wishlist.controller.js';
import { protect } from '../middleware/auth.middleware.js';

const router = Router();

router.get('/', protect, wishlistController.getWishlist);
router.post('/:listingId', protect, wishlistController.addToWishlist);
router.delete('/:listingId', protect, wishlistController.removeFromWishlist);

export default router;
