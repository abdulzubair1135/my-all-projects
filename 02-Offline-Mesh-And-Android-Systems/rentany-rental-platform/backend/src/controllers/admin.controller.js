import pool from '../config/database.js';
import { userRepository } from '../repositories/user.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const adminController = {
  async getDashboard(req, res, next) {
    try {
      // 1. Fetch user counts
      const [[{ total_users }]] = await pool.query("SELECT COUNT(*) as total_users FROM users WHERE status != 'deleted'");
      const [[{ active_users }]] = await pool.query("SELECT COUNT(*) as active_users FROM users WHERE status = 'active'");
      const [[{ suspended_users }]] = await pool.query("SELECT COUNT(*) as suspended_users FROM users WHERE status = 'suspended'");

      // 2. Fetch listings counts
      const [[{ total_listings }]] = await pool.query("SELECT COUNT(*) as total_listings FROM listings WHERE deleted_at IS NULL");
      const [[{ pending_listings }]] = await pool.query("SELECT COUNT(*) as pending_listings FROM listings WHERE status = 'pending_review' AND deleted_at IS NULL");

      // 3. Fetch bookings counts
      const [[{ active_bookings }]] = await pool.query("SELECT COUNT(*) as active_bookings FROM bookings WHERE booking_status = 'active'");
      const [[{ completed_bookings }]] = await pool.query("SELECT COUNT(*) as completed_bookings FROM bookings WHERE booking_status = 'completed'");
      const [[{ cancelled_bookings }]] = await pool.query("SELECT COUNT(*) as cancelled_bookings FROM bookings WHERE booking_status = 'cancelled'");

      // 4. Fetch financial numbers
      const [[{ total_revenue }]] = await pool.query("SELECT COALESCE(SUM(amount), 0) as total_revenue FROM payments WHERE status = 'paid'");
      const [[{ total_deposits }]] = await pool.query("SELECT COALESCE(SUM(amount), 0) as total_deposits FROM deposits WHERE status = 'held'");
      const [[{ total_refunds }]] = await pool.query("SELECT COALESCE(SUM(amount), 0) as total_refunds FROM refunds WHERE status = 'succeeded'");

      // 5. Fetch general metrics
      const [[{ total_reports }]] = await pool.query("SELECT COUNT(*) as total_reports FROM reports WHERE status = 'pending'");
      const [[{ avg_rating }]] = await pool.query("SELECT COALESCE(AVG(rating), 0) as avg_rating FROM reviews WHERE status = 'approved'");

      // 6. Most popular listings (by booking count)
      const [popularListings] = await pool.query(
        `SELECT id, title, price_per_day, booking_count, rating_average 
         FROM listings WHERE deleted_at IS NULL 
         ORDER BY booking_count DESC LIMIT 5`
      );

      // 7. Most rented categories
      const [popularCategories] = await pool.query(
        `SELECT c.id, c.name, COUNT(l.id) as listings_count, SUM(l.booking_count) as total_rentals
         FROM categories c
         JOIN listings l ON c.id = l.category_id
         WHERE l.deleted_at IS NULL
         GROUP BY c.id, c.name
         ORDER BY total_rentals DESC LIMIT 5`
      );

      res.status(200).json({
        success: true,
        data: {
          users: { total: total_users, active: active_users, suspended: suspended_users },
          listings: { total: total_listings, pending: pending_listings },
          bookings: { active: active_bookings, completed: completed_bookings, cancelled: cancelled_bookings },
          finances: { revenue: Number(total_revenue), deposits: Number(total_deposits), refunds: Number(total_refunds) },
          moderation: { pending_reports: total_reports, average_rating: Number(Number(avg_rating).toFixed(2)) },
          popular_listings: popularListings,
          popular_categories: popularCategories
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async suspendUser(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { reason } = req.body;

      if (!reason) throw new AppError('Reason is required to suspend a user.', 400);

      const user = await userRepository.findById(id);
      if (!user) throw new AppError('User not found.', 404);
      if (user.role === 'admin' || user.role === 'super_admin') {
        throw new AppError('Cannot suspend administrative accounts.', 403);
      }

      await userRepository.update(id, { status: 'suspended' });

      // Audit Log
      await pool.query(
        `INSERT INTO audit_logs (admin_id, action, entity_type, entity_id, new_data)
         VALUES (?, 'suspend_user', 'user', ?, ?)`,
        [req.user.id, id, JSON.stringify({ status: 'suspended', reason })]
      );

      res.status(200).json({
        success: true,
        message: 'User account suspended successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async activateUser(req, res, next) {
    try {
      const id = Number(req.params.id);

      const user = await userRepository.findById(id);
      if (!user) throw new AppError('User not found.', 404);

      await userRepository.update(id, { status: 'active' });

      // Audit Log
      await pool.query(
        `INSERT INTO audit_logs (admin_id, action, entity_type, entity_id, new_data)
         VALUES (?, 'activate_user', 'user', ?, ?)`,
        [req.user.id, id, JSON.stringify({ status: 'active' })]
      );

      res.status(200).json({
        success: true,
        message: 'User account activated successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async approveListing(req, res, next) {
    try {
      const id = Number(req.params.id);

      const listing = await listingRepository.findById(id);
      if (!listing) throw new AppError('Listing not found.', 404);

      await listingRepository.update(id, { status: 'published' });

      // Audit Log
      await pool.query(
        `INSERT INTO audit_logs (admin_id, action, entity_type, entity_id, new_data)
         VALUES (?, 'approve_listing', 'listing', ?, ?)`,
        [req.user.id, id, JSON.stringify({ status: 'published' })]
      );

      res.status(200).json({
        success: true,
        message: 'Listing approved and published successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async rejectListing(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { reason } = req.body;

      if (!reason) throw new AppError('Rejection reason is required.', 400);

      const listing = await listingRepository.findById(id);
      if (!listing) throw new AppError('Listing not found.', 404);

      await listingRepository.update(id, { status: 'rejected' });

      // Audit Log
      await pool.query(
        `INSERT INTO audit_logs (admin_id, action, entity_type, entity_id, new_data)
         VALUES (?, 'reject_listing', 'listing', ?, ?)`,
        [req.user.id, id, JSON.stringify({ status: 'rejected', reason })]
      );

      res.status(200).json({
        success: true,
        message: 'Listing rejected successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async getReports(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT r.*, 
                reporter.full_name as reporter_name,
                reported.full_name as reported_user_name,
                l.title as listing_title
         FROM reports r
         JOIN users reporter ON r.reporter_id = reporter.id
         LEFT JOIN users reported ON r.reported_user_id = reported.id
         LEFT JOIN listings l ON r.listing_id = l.id
         ORDER BY r.id DESC`
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async resolveReport(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { action } = req.body; // resolve or reject

      const [report] = await pool.query('SELECT 1 FROM reports WHERE id = ?', [id]);
      if (report.length === 0) throw new AppError('Report not found.', 404);

      const status = action === 'resolve' ? 'resolved' : 'rejected';
      await pool.query(
        'UPDATE reports SET status = ?, resolved_by = ?, resolved_at = NOW() WHERE id = ?',
        [status, req.user.id, id]
      );

      // Audit Log
      await pool.query(
        `INSERT INTO audit_logs (admin_id, action, entity_type, entity_id, new_data)
         VALUES (?, 'resolve_report', 'report', ?, ?)`,
        [req.user.id, id, JSON.stringify({ status })]
      );

      res.status(200).json({
        success: true,
        message: `Report marked as ${status}`
      });
    } catch (err) {
      next(err);
    }
  },

  async getAuditLogs(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT a.*, u.full_name as admin_name 
         FROM audit_logs a
         JOIN users u ON a.admin_id = u.id
         ORDER BY a.id DESC LIMIT 100`
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async createBanner(req, res, next) {
    try {
      const { bannerRepository } = await import('../repositories/banner.repository.js');
      const { title, subtitle, image_url, action_type, action_value, priority } = req.body;
      const bannerId = await bannerRepository.create({ title, subtitle, image_url, action_type, action_value, priority });
      res.status(201).json({
        success: true,
        message: 'Banner created successfully.',
        data: { bannerId }
      });
    } catch (err) {
      next(err);
    }
  },

  async updateBanner(req, res, next) {
    try {
      const { bannerRepository } = await import('../repositories/banner.repository.js');
      const id = Number(req.params.id);
      const success = await bannerRepository.update(id, req.body);
      if (!success) throw new AppError('Banner not found.', 404);
      res.status(200).json({
        success: true,
        message: 'Banner updated successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async deleteBanner(req, res, next) {
    try {
      const { bannerRepository } = await import('../repositories/banner.repository.js');
      const id = Number(req.params.id);
      const success = await bannerRepository.delete(id);
      if (!success) throw new AppError('Banner not found.', 404);
      res.status(200).json({
        success: true,
        message: 'Banner deleted successfully.'
      });
    } catch (err) {
      next(err);
    }
  },

  async getAllUsers(req, res, next) {
    try {
      const [rows] = await pool.query(
        "SELECT id, email, full_name, role, status, last_active_at, created_at FROM users WHERE status != 'deleted' ORDER BY id DESC"
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async getAllListings(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT l.id, l.title, l.price_per_day, l.status, l.created_at, u.full_name as owner_name, c.name as category_name
         FROM listings l
         JOIN users u ON l.owner_id = u.id
         JOIN categories c ON l.category_id = c.id
         WHERE l.deleted_at IS NULL
         ORDER BY l.id DESC`
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async getAllBookings(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT b.id, b.start_date, b.end_date, b.total_amount, b.booking_status, b.created_at,
                renter.full_name as renter_name, owner.full_name as owner_name, l.title as listing_title
         FROM bookings b
         JOIN users renter ON b.renter_id = renter.id
         JOIN users owner ON b.owner_id = owner.id
         JOIN listings l ON b.listing_id = l.id
         ORDER BY b.id DESC`
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async getAllPayments(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT p.id, p.booking_id, p.amount, p.payment_method, p.status, p.created_at, u.full_name as user_name
         FROM payments p
         JOIN bookings b ON p.booking_id = b.id
         JOIN users u ON b.renter_id = u.id
         ORDER BY p.id DESC`
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async getAllCategories(req, res, next) {
    try {
      const [rows] = await pool.query('SELECT * FROM categories ORDER BY id ASC');
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllReviews(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT r.*, reviewer.full_name as reviewer_name, l.title as listing_title
         FROM reviews r
         JOIN users reviewer ON r.reviewer_id = reviewer.id
         JOIN listings l ON r.listing_id = l.id
         ORDER BY r.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllDeposits(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT d.*, u.full_name as user_name FROM deposits d
         JOIN users u ON d.renter_id = u.id
         ORDER BY d.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllRefunds(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT r.*, u.full_name as user_name FROM refunds r
         JOIN bookings b ON r.booking_id = b.id
         JOIN users u ON b.renter_id = u.id
         ORDER BY r.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllNotifications(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT n.*, u.full_name as user_name FROM notifications n
         JOIN users u ON n.user_id = u.id
         ORDER BY n.id DESC LIMIT 200`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllWishlists(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT w.*, u.full_name as user_name, l.title as listing_title
         FROM wishlists w
         JOIN users u ON w.user_id = u.id
         JOIN listings l ON w.listing_id = l.id
         ORDER BY w.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllConversations(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT c.*, l.title as listing_title FROM conversations c
         JOIN listings l ON c.listing_id = l.id
         ORDER BY c.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllMessages(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT m.*, u.full_name as sender_name FROM messages m
         JOIN users u ON m.sender_id = u.id
         ORDER BY m.id DESC LIMIT 200`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllBanners(req, res, next) {
    try {
      const [rows] = await pool.query('SELECT * FROM banners ORDER BY priority ASC');
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async getAllListingImages(req, res, next) {
    try {
      const [rows] = await pool.query(
        `SELECT li.*, l.title as listing_title FROM listing_images li
         JOIN listings l ON li.listing_id = l.id
         ORDER BY li.id DESC`
      );
      res.status(200).json({ success: true, data: rows });
    } catch (err) { next(err); }
  },

  async createAdminUser(req, res, next) {
    try {
      const { email, full_name, phone, password, role, status } = req.body;
      if (!email || !full_name || !phone || !password) {
        throw new AppError('Missing required fields for user creation.', 400);
      }
      const crypto = await import('crypto');
      const bcrypt = await import('bcryptjs');
      const passwordHash = await bcrypt.default.hash(password, 10);
      const uuid = crypto.randomUUID();
      
      const [result] = await pool.query(
        'INSERT INTO users (uuid, email, full_name, phone, password_hash, role, status, email_verified, phone_verified) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)',
        [uuid, email, full_name, phone, passwordHash, role || 'user', status || 'active']
      );
      res.status(201).json({ success: true, message: 'User created successfully.', data: { id: result.insertId } });
    } catch (err) { next(err); }
  },

  async updateAdminUser(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { email, full_name, phone, role, status } = req.body;
      const [result] = await pool.query(
        'UPDATE users SET email = ?, full_name = ?, phone = ?, role = ?, status = ? WHERE id = ?',
        [email, full_name, phone, role, status, id]
      );
      if (result.affectedRows === 0) throw new AppError('User not found.', 404);
      res.status(200).json({ success: true, message: 'User updated successfully.' });
    } catch (err) { next(err); }
  },

  async deleteAdminUser(req, res, next) {
    try {
      const id = Number(req.params.id);
      const [result] = await pool.query("UPDATE users SET status = 'deleted' WHERE id = ?", [id]);
      if (result.affectedRows === 0) throw new AppError('User not found.', 404);
      res.status(200).json({ success: true, message: 'User deleted successfully.' });
    } catch (err) { next(err); }
  },

  async createAdminListing(req, res, next) {
    try {
      const { owner_id, category_id, title, description, price_per_day, status, location } = req.body;
      if (!owner_id || !category_id || !title || !price_per_day) {
        throw new AppError('Missing required fields for listing creation.', 400);
      }
      const crypto = await import('crypto');
      const uuid = crypto.randomUUID();
      
      const [result] = await pool.query(
        'INSERT INTO listings (uuid, owner_id, category_id, title, description, price_per_day, status, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        [uuid, owner_id, category_id, title, description || '', price_per_day, status || 'pending', location || '']
      );
      res.status(201).json({ success: true, message: 'Listing created successfully.', data: { id: result.insertId } });
    } catch (err) { next(err); }
  },

  async updateAdminListing(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { category_id, title, description, price_per_day, status, location } = req.body;
      const [result] = await pool.query(
        'UPDATE listings SET category_id = ?, title = ?, description = ?, price_per_day = ?, status = ?, location = ? WHERE id = ?',
        [category_id, title, description || '', price_per_day, status, location || '', id]
      );
      if (result.affectedRows === 0) throw new AppError('Listing not found.', 404);
      res.status(200).json({ success: true, message: 'Listing updated successfully.' });
    } catch (err) { next(err); }
  },

  async deleteAdminListing(req, res, next) {
    try {
      const id = Number(req.params.id);
      const [result] = await pool.query('UPDATE listings SET deleted_at = NOW() WHERE id = ?', [id]);
      if (result.affectedRows === 0) throw new AppError('Listing not found.', 404);
      res.status(200).json({ success: true, message: 'Listing deleted successfully.' });
    } catch (err) { next(err); }
  }
};

