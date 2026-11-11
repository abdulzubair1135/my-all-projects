import pool from '../config/database.js';
import { bookingRepository } from '../repositories/booking.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { notificationRepository } from '../repositories/notification.repository.js';
import { pricingService } from './pricing.service.js';
import { AppError } from '../middleware/error.middleware.js';
import crypto from 'crypto';

export const bookingService = {
  async createBooking(renterId, bookingData) {
    const { listingId, startDate, endDate, deliveryType, quantity = 1 } = bookingData;

    // Validate dates
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (start < today) {
      throw new AppError('Booking start date cannot be in the past.', 400);
    }
    if (end <= start) {
      throw new AppError('Booking end date must be after the start date.', 400);
    }

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      // 1. Lock listing row for writing to prevent race conditions (double-booking protection)
      const listing = await bookingRepository.lockListing(connection, listingId);
      if (!listing) {
        throw new AppError('The requested listing does not exist.', 404);
      }

      // 2. Verify listing is active/published
      if (listing.status !== 'published') {
        throw new AppError('This item is currently unavailable for rent.', 400);
      }

      // 3. User cannot rent their own listing
      if (listing.owner_id === renterId) {
        throw new AppError('You cannot rent your own listing.', 400);
      }

      // 4. Check requested rental days limits
      const rentalDays = pricingService.calculateRentalDays(startDate, endDate);
      if (rentalDays < listing.minimum_rental_days) {
        throw new AppError(`Minimum rental period is ${listing.minimum_rental_days} days.`, 400);
      }
      if (rentalDays > listing.maximum_rental_days) {
        throw new AppError(`Maximum rental period is ${listing.maximum_rental_days} days.`, 400);
      }

      // 5. Verify no overlapping bookings (Double-booking protection)
      const overlapping = await bookingRepository.getOverlappingBookings(connection, listingId, startDate, endDate);
      if (overlapping.length > 0) {
        throw new AppError('The listing is already booked for the selected dates.', 409);
      }

      // 6. Calculate prices on server side
      const pricing = pricingService.calculatePrice({
        pricePerDay: listing.price_per_day,
        rentalDays,
        quantity,
        deliveryAvailable: listing.delivery_available,
        deliveryType,
        deliveryFee: listing.delivery_fee,
        depositPerItem: listing.refundable_deposit
      });

      // 7. Create booking record
      const uuid = crypto.randomUUID();
      const booking = {
        uuid,
        listing_id: listingId,
        renter_id: renterId,
        owner_id: listing.owner_id,
        start_date: startDate,
        end_date: endDate,
        rental_days: pricing.rentalDays,
        price_per_day: pricing.pricePerDay,
        subtotal: pricing.subtotal,
        delivery_fee: pricing.deliveryFee,
        service_fee: pricing.serviceFee,
        discount: pricing.discount,
        deposit_amount: pricing.depositAmount,
        total_amount: pricing.totalAmount,
        payment_status: 'pending',
        booking_status: 'pending'
      };

      const bookingId = await bookingRepository.createBooking(connection, booking);

      // 8. Create booking item snapshot
      const snapshot = {
        booking_id: bookingId,
        listing_id: listingId,
        listing_title: listing.title,
        price_per_day: pricing.pricePerDay,
        quantity,
        rental_days: pricing.rentalDays,
        subtotal: pricing.subtotal
      };
      await bookingRepository.createBookingItemSnapshot(connection, bookingId, snapshot);

      // 9. Reserve listing availability
      const availability = {
        listing_id: listingId,
        start_date: startDate,
        end_date: endDate,
        status: 'booked',
        booking_id: bookingId
      };
      await bookingRepository.addAvailabilityBlock(connection, availability);

      // 10. Generate mock payment hold record
      await connection.query(
        `INSERT INTO payments (booking_id, user_id, transaction_id, provider, amount, currency, status)
         VALUES (?, ?, ?, 'stripe', ?, 'INR', 'pending')`,
        [bookingId, renterId, `tx_mock_${crypto.randomBytes(8).toString('hex')}`, pricing.totalAmount]
      );

      // 11. Create Security Deposit hold record if deposit is required
      if (pricing.depositAmount > 0) {
        await connection.query(
          `INSERT INTO deposits (booking_id, renter_id, owner_id, amount, status, hold_reference)
           VALUES (?, ?, ?, ?, 'held', ?)`,
          [bookingId, renterId, listing.owner_id, pricing.depositAmount, `dep_mock_${crypto.randomBytes(8).toString('hex')}`]
        );
      }

      // Commit transaction
      await connection.commit();

      // 12. Create background notification (outside transaction so it doesn't block if notification fails)
      try {
        await notificationRepository.create(
          listing.owner_id,
          'booking_created',
          'New Booking Request',
          `You have a new booking request for your item "${listing.title}".`,
          { bookingId, bookingUuid: uuid }
        );
      } catch (err) {
        console.error('Notification failed:', err.message);
      }

      return await bookingRepository.findById(bookingId);
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  },

  async confirmBooking(bookingId, ownerId) {
    const booking = await bookingRepository.findById(bookingId);
    if (!booking) throw new AppError('Booking not found.', 404);
    if (booking.owner_id !== ownerId) throw new AppError('Only the listing owner can confirm this booking.', 403);
    if (booking.booking_status !== 'pending') throw new AppError('Only pending bookings can be confirmed.', 400);

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      // Update booking status
      await bookingRepository.updateBookingStatus(connection, bookingId, {
        booking_status: 'confirmed',
        payment_status: 'paid', // Simulate payment successful upon confirmation
        confirmed_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      });

      // Update payment record to paid
      await connection.query(
        "UPDATE payments SET status = 'paid', paid_at = NOW() WHERE booking_id = ?",
        [bookingId]
      );

      // Increment listing booking count
      await connection.query('UPDATE listings SET booking_count = booking_count + 1 WHERE id = ?', [booking.listing_id]);

      await connection.commit();

      // Send notifications
      await notificationRepository.create(
        booking.renter_id,
        'booking_confirmed',
        'Booking Confirmed!',
        `Your booking for "${booking.listing_title}" has been confirmed by the owner.`,
        { bookingId }
      );

      // Send email to renter
      const { emailService } = await import('./email.service.js');
      emailService.sendBookingConfirmationEmail(booking.renter_email, booking.renter_name, {
        listingTitle: booking.listing_title,
        startDate: booking.start_date,
        endDate: booking.end_date,
        rentalDays: booking.rental_days,
        depositAmount: booking.deposit_amount,
        totalPrice: booking.total_amount
      }).catch(err => console.error('Failed to send booking confirmation email:', err.message));
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  },

  async startBooking(bookingId, ownerId) {
    // Renter picks up or receives delivery
    const booking = await bookingRepository.findById(bookingId);
    if (!booking) throw new AppError('Booking not found.', 404);
    if (booking.owner_id !== ownerId) throw new AppError('Only the listing owner can start this rental handover.', 403);
    if (booking.booking_status !== 'confirmed') throw new AppError('Handover can only be started for confirmed bookings.', 400);

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      await bookingRepository.updateBookingStatus(connection, bookingId, {
        booking_status: 'active',
        started_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      });

      await connection.commit();

      await notificationRepository.create(
        booking.renter_id,
        'rental_started',
        'Rental Handover Complete',
        `Your rental for "${booking.listing_title}" has started. Keep it safe!`,
        { bookingId }
      );
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  },

  async returnBooking(bookingId, ownerId) {
    // Owner registers that the item is returned
    const booking = await bookingRepository.findById(bookingId);
    if (!booking) throw new AppError('Booking not found.', 404);
    if (booking.owner_id !== ownerId) throw new AppError('Only the listing owner can register the return.', 403);
    if (booking.booking_status !== 'active') throw new AppError('Only active rentals can be marked as returned.', 400);

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      await bookingRepository.updateBookingStatus(connection, bookingId, {
        booking_status: 'returned',
        returned_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      });

      await connection.commit();

      await notificationRepository.create(
        booking.renter_id,
        'rental_returned',
        'Item Marked as Returned',
        `The owner confirmed the return of "${booking.listing_title}". Security deposit will be processed next.`,
        { bookingId }
      );
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  },

  async completeBooking(bookingId, ownerId) {
    // Owner completes booking, releasing deposit
    const booking = await bookingRepository.findById(bookingId);
    if (!booking) throw new AppError('Booking not found.', 404);
    if (booking.owner_id !== ownerId) throw new AppError('Only the listing owner can complete the booking.', 403);
    if (booking.booking_status !== 'returned') throw new AppError('Rental must be returned before completing.', 400);

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      // 1. Complete Booking status
      await bookingRepository.updateBookingStatus(connection, bookingId, {
        booking_status: 'completed',
        completed_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      });

      // 2. Release availability dates
      await bookingRepository.removeAvailabilityBlock(connection, bookingId);

      // 3. Release Security Deposit (Simulated)
      await connection.query(
        "UPDATE deposits SET status = 'released', released_at = NOW() WHERE booking_id = ?",
        [bookingId]
      );

      await connection.commit();

      await notificationRepository.create(
        booking.renter_id,
        'booking_completed',
        'Rental Completed',
        `Your booking for "${booking.listing_title}" is completed. Thank you! Please write a review.`,
        { bookingId }
      );
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  },

  async cancelBooking(bookingId, userId, reason) {
    const booking = await bookingRepository.findById(bookingId);
    if (!booking) throw new AppError('Booking not found.', 404);

    // Renter or owner can cancel
    const isRenter = booking.renter_id === userId;
    const isOwner = booking.owner_id === userId;
    if (!isRenter && !isOwner) {
      throw new AppError('You are not authorized to cancel this booking.', 403);
    }

    // Cancel rules: only pending or confirmed can be cancelled (cannot cancel active/returned/completed)
    const activeStates = ['active', 'returned', 'completed', 'cancelled', 'rejected'];
    if (activeStates.includes(booking.booking_status)) {
      throw new AppError(`Cannot cancel a booking in "${booking.booking_status}" state.`, 400);
    }

    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();

      // 1. Update Booking status to cancelled
      await bookingRepository.updateBookingStatus(connection, bookingId, {
        booking_status: 'cancelled',
        payment_status: booking.payment_status === 'paid' ? 'refunded' : 'failed',
        cancellation_reason: reason,
        cancelled_by: userId,
        cancelled_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      });

      // 2. Release dates from availability calendar
      await bookingRepository.removeAvailabilityBlock(connection, bookingId);

      // 3. Release deposit if any
      await connection.query(
        "UPDATE deposits SET status = 'released', released_at = NOW() WHERE booking_id = ? AND status = 'held'",
        [bookingId]
      );

      // 4. Create refund record if they already paid
      if (booking.payment_status === 'paid') {
        const [paymentRow] = await connection.query(
          "SELECT id FROM payments WHERE booking_id = ? AND status = 'paid'",
          [bookingId]
        );
        if (paymentRow.length > 0) {
          const paymentId = paymentRow[0].id;
          await connection.query(
            `INSERT INTO refunds (payment_id, booking_id, amount, reason, status, processed_at)
             VALUES (?, ?, ?, ?, 'succeeded', NOW())`,
            [paymentId, bookingId, booking.total_amount, `Cancellation: ${reason}`]
          );
          await connection.query(
            "UPDATE payments SET status = 'refunded', refunded_at = NOW() WHERE id = ?",
            [paymentId]
          );
        }
      }

      await connection.commit();

      // Notify the other participant
      const notifyUser = isRenter ? booking.owner_id : booking.renter_id;
      await notificationRepository.create(
        notifyUser,
        'booking_cancelled',
        'Booking Cancelled',
        `Booking for "${booking.listing_title}" was cancelled by the other party: "${reason}".`,
        { bookingId }
      );

      // Send cancellation emails to both parties
      const { emailService } = await import('./email.service.js');
      emailService.sendBookingStatusEmail(booking.renter_email, booking.renter_name, booking.listing_title, 'cancelled')
        .catch(err => console.error('Renter cancellation email failed:', err.message));
      emailService.sendBookingStatusEmail(booking.owner_email, booking.owner_name, booking.listing_title, 'cancelled')
        .catch(err => console.error('Owner cancellation email failed:', err.message));

    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  }
};
