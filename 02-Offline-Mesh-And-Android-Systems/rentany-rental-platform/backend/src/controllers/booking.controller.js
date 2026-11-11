import { bookingService } from '../services/booking.service.js';
import { bookingRepository } from '../repositories/booking.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const bookingController = {
  async createBooking(req, res, next) {
    try {
      const renterId = req.user.id;
      const newBooking = await bookingService.createBooking(renterId, req.body);
      
      res.status(201).json({
        success: true,
        message: 'Booking request created successfully',
        data: newBooking
      });
    } catch (err) {
      next(err);
    }
  },

  async getBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      const booking = await bookingRepository.findById(id);
      
      if (!booking) {
        throw new AppError('Booking not found.', 404);
      }

      // Check if user is either renter or owner
      if (booking.renter_id !== req.user.id && booking.owner_id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'super_admin') {
        throw new AppError('You are not authorized to view this booking.', 403);
      }

      res.status(200).json({
        success: true,
        data: booking
      });
    } catch (err) {
      next(err);
    }
  },

  async getMyBookings(req, res, next) {
    try {
      const { type = 'renter', filter = 'all' } = req.query; // type: renter or owner
      const bookings = await bookingRepository.getUserBookings(req.user.id, type, filter);
      
      res.status(200).json({
        success: true,
        data: bookings
      });
    } catch (err) {
      next(err);
    }
  },

  async cancelBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { reason } = req.body;

      if (!reason) {
        throw new AppError('Cancellation reason is required.', 400);
      }

      await bookingService.cancelBooking(id, req.user.id, reason);

      res.status(200).json({
        success: true,
        message: 'Booking cancelled successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async confirmBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      await bookingService.confirmBooking(id, req.user.id);
      
      res.status(200).json({
        success: true,
        message: 'Booking confirmed successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async startBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      await bookingService.startBooking(id, req.user.id);

      res.status(200).json({
        success: true,
        message: 'Handover complete. Rental is now active.'
      });
    } catch (err) {
      next(err);
    }
  },

  async returnBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      await bookingService.returnBooking(id, req.user.id);

      res.status(200).json({
        success: true,
        message: 'Item registered as returned.'
      });
    } catch (err) {
      next(err);
    }
  },

  async completeBooking(req, res, next) {
    try {
      const id = Number(req.params.id);
      await bookingService.completeBooking(id, req.user.id);

      res.status(200).json({
        success: true,
        message: 'Rental completed and deposit processing finished.'
      });
    } catch (err) {
      next(err);
    }
  }
};
