import { userRepository } from '../repositories/user.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { bookingRepository } from '../repositories/booking.repository.js';
import { reviewRepository } from '../repositories/review.repository.js';
import { wishlistRepository } from '../repositories/wishlist.repository.js';
import { AppError } from '../middleware/error.middleware.js';
import pool from '../config/database.js';

export const userController = {
  async getProfile(req, res, next) {
    try {
      const user = await userRepository.findById(req.user.id);
      if (!user) throw new AppError('Profile not found', 404);
      
      const addresses = await userRepository.getAddresses(user.id);
      user.addresses = addresses;
      
      delete user.password_hash;
      
      res.status(200).json({
        success: true,
        data: user
      });
    } catch (err) {
      next(err);
    }
  },

  async updateProfile(req, res, next) {
    try {
      const { full_name, email, phone } = req.body;
      
      // Check email uniqueness if modified
      if (email && email !== req.user.email) {
        const existing = await userRepository.findByEmail(email);
        if (existing) throw new AppError('Email is already in use.', 400);
      }

      // Check phone uniqueness if modified
      if (phone && phone !== req.user.phone) {
        const existing = await userRepository.findByPhone(phone);
        if (existing) throw new AppError('Phone number is already in use.', 400);
      }

      await userRepository.update(req.user.id, { full_name, email, phone });
      
      const updated = await userRepository.findById(req.user.id);
      delete updated.password_hash;

      res.status(200).json({
        success: true,
        message: 'Profile updated successfully',
        data: updated
      });
    } catch (err) {
      next(err);
    }
  },

  async uploadProfileImage(req, res, next) {
    try {
      if (!req.file) {
        throw new AppError('Please upload an image file.', 400);
      }

      const { uploadToCloudinary } = await import('../middleware/upload.middleware.js');
      const uploadResult = await uploadToCloudinary(req.file.buffer);
      const imageUrl = uploadResult.secure_url;
      
      await userRepository.update(req.user.id, { profile_image: imageUrl });

      res.status(200).json({
        success: true,
        message: 'Profile image updated successfully',
        data: { imageUrl }
      });
    } catch (err) {
      next(err);
    }
  },

  async getPublicProfile(req, res, next) {
    try {
      const userId = Number(req.params.id);
      const user = await userRepository.findById(userId);
      if (!user || user.status !== 'active') {
        throw new AppError('User not found or is inactive.', 404);
      }

      // Return only public fields
      const publicUser = {
        id: user.id,
        full_name: user.full_name,
        profile_image: user.profile_image,
        created_at: user.created_at,
        role: user.role
      };

      // Also get their public listings
      const [listings] = await pool.query(
        "SELECT id, title, price_per_day, rating_average, rating_count, status FROM listings WHERE owner_id = ? AND status = 'published' AND deleted_at IS NULL",
        [userId]
      );

      res.status(200).json({
        success: true,
        data: {
          profile: publicUser,
          listings
        }
      });
    } catch (err) {
      next(err);
    }
  },

  // Address CRUD
  async getAddresses(req, res, next) {
    try {
      const addresses = await userRepository.getAddresses(req.user.id);
      res.status(200).json({
        success: true,
        data: addresses
      });
    } catch (err) {
      next(err);
    }
  },

  async addAddress(req, res, next) {
    try {
      const { address_line, city, state, country, postal_code, latitude, longitude, is_default } = req.body;
      const addressId = await userRepository.createAddress(req.user.id, {
        address_line, city, state, country, postal_code, latitude, longitude, is_default
      });

      const addresses = await userRepository.getAddresses(req.user.id);
      res.status(201).json({
        success: true,
        message: 'Address added successfully',
        data: addresses
      });
    } catch (err) {
      next(err);
    }
  },

  async deleteAddress(req, res, next) {
    try {
      const addressId = Number(req.params.id);
      const success = await userRepository.deleteAddress(addressId, req.user.id);
      
      if (!success) {
        throw new AppError('Address not found or unauthorized.', 404);
      }

      const addresses = await userRepository.getAddresses(req.user.id);
      res.status(200).json({
        success: true,
        message: 'Address deleted successfully',
        data: addresses
      });
    } catch (err) {
      next(err);
    }
  },

  async setDefaultAddress(req, res, next) {
    try {
      const addressId = Number(req.params.id);
      const success = await userRepository.setDefaultAddress(addressId, req.user.id);

      if (!success) {
        throw new AppError('Address not found or unauthorized.', 404);
      }

      const addresses = await userRepository.getAddresses(req.user.id);
      res.status(200).json({
        success: true,
        message: 'Default address updated successfully',
        data: addresses
      });
    } catch (err) {
      next(err);
    }
  },

  // Relations
  async getMyListings(req, res, next) {
    try {
      const [listings] = await pool.query(
        "SELECT l.*, c.name as category_name, (SELECT image_url FROM listing_images WHERE listing_id = l.id AND is_primary = 1 LIMIT 1) as listing_primary_image FROM listings l JOIN categories c ON l.category_id = c.id WHERE l.owner_id = ? AND l.deleted_at IS NULL ORDER BY l.id DESC",
        [req.user.id]
      );
      res.status(200).json({
        success: true,
        data: listings
      });
    } catch (err) {
      next(err);
    }
  },

  async getMyBookings(req, res, next) {
    try {
      const { filter } = req.query; // upcoming, ongoing, completed
      const bookings = await bookingRepository.getUserBookings(req.user.id, 'renter', filter);
      res.status(200).json({
        success: true,
        data: bookings
      });
    } catch (err) {
      next(err);
    }
  },

  async getMyReviews(req, res, next) {
    try {
      const [reviews] = await pool.query(
        "SELECT r.*, l.title as listing_title FROM reviews r JOIN listings l ON r.listing_id = l.id WHERE r.reviewer_id = ? ORDER BY r.id DESC",
        [req.user.id]
      );
      res.status(200).json({
        success: true,
        data: reviews
      });
    } catch (err) {
      next(err);
    }
  },

  async getMyWishlist(req, res, next) {
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

  async deleteProfile(req, res, next) {
    // Soft-delete user profile
    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();
      
      const userId = req.user.id;
      
      // 1. Soft delete user
      await connection.query(
        "UPDATE users SET status = 'deleted' WHERE id = ?",
        [userId]
      );

      // 2. Archive all listings owned by this user
      await connection.query(
        "UPDATE listings SET status = 'archived', deleted_at = NOW() WHERE owner_id = ?",
        [userId]
      );
      
      await connection.commit();
      res.status(200).json({
        success: true,
        message: 'Account and associated listings deleted successfully.'
      });
    } catch (err) {
      await connection.rollback();
      next(err);
    } finally {
      connection.release();
    }
  }
};
