import { wishlistRepository } from '../repositories/wishlist.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const wishlistController = {
  async getWishlist(req, res, next) {
    try {
      const wishlist = await wishlistRepository.getUserWishlist(req.user.id);
      res.status(200).json({
        success: true,
        data: wishlist
      });
    } catch (err) {
      next(err);
    }
  },

  async addToWishlist(req, res, next) {
    try {
      const listingId = Number(req.params.listingId);

      // Verify listing exists
      const listing = await listingRepository.findById(listingId);
      if (!listing) {
        throw new AppError('Listing not found.', 404);
      }

      try {
        await wishlistRepository.add(req.user.id, listingId);
      } catch (err) {
        // If MySQL UNIQUE constraint error, it means already wishlisted. Ignore and succeed.
        if (err.code !== 'ER_DUP_ENTRY') throw err;
      }

      res.status(200).json({
        success: true,
        message: 'Item added to wishlist.'
      });
    } catch (err) {
      next(err);
    }
  },

  async removeFromWishlist(req, res, next) {
    try {
      const listingId = Number(req.params.listingId);
      const success = await wishlistRepository.remove(req.user.id, listingId);

      if (!success) {
        throw new AppError('Listing not found in your wishlist.', 404);
      }

      res.status(200).json({
        success: true,
        message: 'Item removed from wishlist.'
      });
    } catch (err) {
      next(err);
    }
  }
};
