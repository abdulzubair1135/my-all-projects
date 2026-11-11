import pool from '../config/database.js';

export const wishlistRepository = {
  async getUserWishlist(userId) {
    const [rows] = await pool.query(
      `SELECT w.id as wishlist_entry_id, w.created_at as wishlisted_at,
              l.*, 
              c.name as category_name,
              li.image_url as listing_primary_image
       FROM wishlists w
       JOIN listings l ON w.listing_id = l.id
       JOIN categories c ON l.category_id = c.id
       LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
       WHERE w.user_id = ? AND l.deleted_at IS NULL
       ORDER BY w.id DESC`,
      [userId]
    );
    return rows;
  },

  async add(userId, listingId) {
    // INSERT IGNORE or standard INSERT. Since we have UNIQUE constraint, standard INSERT throws error if exists
    const [res] = await pool.query(
      'INSERT INTO wishlists (user_id, listing_id) VALUES (?, ?)',
      [userId, listingId]
    );
    return res.insertId;
  },

  async remove(userId, listingId) {
    const [res] = await pool.query(
      'DELETE FROM wishlists WHERE user_id = ? AND listing_id = ?',
      [userId, listingId]
    );
    return res.affectedRows > 0;
  }
};
