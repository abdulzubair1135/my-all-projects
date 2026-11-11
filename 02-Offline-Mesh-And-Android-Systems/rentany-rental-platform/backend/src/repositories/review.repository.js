import pool from '../config/database.js';

export const reviewRepository = {
  async getListingReviews(listingId) {
    const [rows] = await pool.query(
      `SELECT r.*, u.full_name as reviewer_name, u.profile_image as reviewer_image
       FROM reviews r
       JOIN users u ON r.reviewer_id = u.id
       WHERE r.listing_id = ? AND r.status = 'approved'
       ORDER BY r.id DESC`,
      [listingId]
    );
    return rows;
  },

  async hasReviewedBooking(bookingId, reviewerId) {
    const [rows] = await pool.query(
      'SELECT 1 FROM reviews WHERE booking_id = ? AND reviewer_id = ?',
      [bookingId, reviewerId]
    );
    return rows.length > 0;
  },

  async create(review) {
    const { booking_id, listing_id, reviewer_id, owner_id, rating, title, comment } = review;
    const [res] = await pool.query(
      `INSERT INTO reviews (booking_id, listing_id, reviewer_id, owner_id, rating, title, comment, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, 'approved')`,
      [booking_id, listing_id, reviewer_id, owner_id, rating, title, comment]
    );
    return res.insertId;
  },

  async updateStatus(id, status) {
    const [res] = await pool.query(
      'UPDATE reviews SET status = ? WHERE id = ?',
      [status, id]
    );
    return res.affectedRows > 0;
  },

  async getAdminReviews({ limit = 20, offset = 0, status }) {
    let query = `
      SELECT r.*, u.full_name as reviewer_name, o.full_name as owner_name, l.title as listing_title
      FROM reviews r
      JOIN users u ON r.reviewer_id = u.id
      JOIN users o ON r.owner_id = o.id
      JOIN listings l ON r.listing_id = l.id
      WHERE 1=1
    `;
    const params = [];

    if (status) {
      query += ' AND r.status = ?';
      params.push(status);
    }

    query += ' ORDER BY r.id DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const [rows] = await pool.query(query, params);
    
    let countQuery = 'SELECT COUNT(*) as total FROM reviews WHERE 1=1';
    const countParams = [];
    if (status) {
      countQuery += ' AND status = ?';
      countParams.push(status);
    }
    const [[{ total }]] = await pool.query(countQuery, countParams);

    return { reviews: rows, total };
  }
};
