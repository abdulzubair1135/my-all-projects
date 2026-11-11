import { reviewRepository } from '../repositories/review.repository.js';
import { bookingRepository } from '../repositories/booking.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const reviewController = {
  async getListingReviews(req, res, next) {
    try {
      const listingId = Number(req.params.listingId);
      const reviews = await reviewRepository.getListingReviews(listingId);

      res.status(200).json({
        success: true,
        data: reviews
      });
    } catch (err) {
      next(err);
    }
  },

  async createReview(req, res, next) {
    try {
      const { bookingId, rating, title, comment } = req.body;
      const reviewerId = req.user.id;

      // 1. Fetch booking
      const booking = await bookingRepository.findById(bookingId);
      if (!booking) {
        throw new AppError('Associated booking not found.', 404);
      }

      // 2. Business Rule: Renter can only review after completion
      if (booking.renter_id !== reviewerId) {
        throw new AppError('You are not authorized to review this booking.', 403);
      }

      if (booking.booking_status !== 'completed' && booking.booking_status !== 'returned') {
        throw new AppError('You can only review a listing after the rental is completed or returned.', 400);
      }

      // 3. Business Rule: User cannot review their own listing
      if (booking.owner_id === reviewerId) {
        throw new AppError('You cannot review your own listing.', 400);
      }

      // 4. Business Rule: One review per booking/listing/user
      const alreadyReviewed = await reviewRepository.hasReviewedBooking(bookingId, reviewerId);
      if (alreadyReviewed) {
        throw new AppError('You have already submitted a review for this booking.', 400);
      }

      // 5. Create Review
      const reviewId = await reviewRepository.create({
        booking_id: bookingId,
        listing_id: booking.listing_id,
        reviewer_id: reviewerId,
        owner_id: booking.owner_id,
        rating,
        title,
        comment
      });

      // 6. Update listing rating aggregates
      await listingRepository.updateListingRating(booking.listing_id);

      res.status(201).json({
        success: true,
        message: 'Review submitted successfully',
        data: { reviewId }
      });
    } catch (err) {
      next(err);
    }
  }
};
