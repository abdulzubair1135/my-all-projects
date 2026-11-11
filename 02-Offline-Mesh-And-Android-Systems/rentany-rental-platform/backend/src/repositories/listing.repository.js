import pool from '../config/database.js';

export const listingRepository = {
  async findById(id, authedUserId = null) {
    // 1. Fetch listing details and category name
    const [rows] = await pool.query(
      `SELECT l.*, c.name as category_name, c.slug as category_slug, 
              u.full_name as owner_name, u.profile_image as owner_image, u.created_at as owner_since
       FROM listings l
       JOIN categories c ON l.category_id = c.id
       JOIN users u ON l.owner_id = u.id
       WHERE l.id = ? AND l.deleted_at IS NULL`,
      [id]
    );
    
    if (rows.length === 0) return null;
    const listing = rows[0];

    // 2. Fetch images
    const [images] = await pool.query(
      'SELECT id, image_url, sort_order, is_primary FROM listing_images WHERE listing_id = ? ORDER BY sort_order ASC, id ASC',
      [id]
    );
    listing.images = images;

    // 3. Fetch attributes
    const [attributes] = await pool.query(
      'SELECT id, attribute_name, attribute_value FROM listing_attributes WHERE listing_id = ?',
      [id]
    );
    listing.attributes = attributes;

    // 4. Fetch availability blocks
    const [availability] = await pool.query(
      'SELECT start_date, end_date, status FROM listing_availability WHERE listing_id = ? ORDER BY start_date ASC',
      [id]
    );
    listing.availability = availability;

    // 5. Check if wishlisted by authenticated user
    listing.isBookmarked = false;
    if (authedUserId) {
      const [wishlist] = await pool.query(
        'SELECT 1 FROM wishlists WHERE user_id = ? AND listing_id = ?',
        [authedUserId, id]
      );
      listing.isBookmarked = wishlist.length > 0;
    }

    return listing;
  },

  async create(listing) {
    const {
      uuid, owner_id, category_id, title, slug, description, price_per_day,
      price_per_hour = null, refundable_deposit = 0.00, quantity = 1, condition = 'Good',
      location_address, city, state, country, postal_code, latitude, longitude,
      delivery_available = 0, delivery_fee = 0.00, pickup_available = 1, instant_booking = 0,
      minimum_rental_days = 1, maximum_rental_days = 365, status = 'published'
    } = listing;

    const [res] = await pool.query(
      `INSERT INTO listings (uuid, owner_id, category_id, title, slug, description, price_per_day,
        price_per_hour, refundable_deposit, quantity, \`condition\`, location_address, city, state, country,
        postal_code, latitude, longitude, delivery_available, delivery_fee, pickup_available, instant_booking,
        minimum_rental_days, maximum_rental_days, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [uuid, owner_id, category_id, title, slug, description, price_per_day,
        price_per_hour, refundable_deposit, quantity, condition, location_address, city, state, country,
        postal_code, latitude, longitude, delivery_available, delivery_fee, pickup_available, instant_booking,
        minimum_rental_days, maximum_rental_days, status]
    );
    return res.insertId;
  },

  async update(id, listing) {
    const fields = [];
    const values = [];

    const allowed = [
      'category_id', 'title', 'slug', 'description', 'price_per_day', 'price_per_hour',
      'refundable_deposit', 'quantity', 'condition', 'location_address', 'city', 'state',
      'country', 'postal_code', 'latitude', 'longitude', 'delivery_available', 'delivery_fee',
      'pickup_available', 'instant_booking', 'minimum_rental_days', 'maximum_rental_days', 'status'
    ];

    for (const key of allowed) {
      if (listing[key] !== undefined) {
        fields.push(`\`${key}\` = ?`);
        values.push(listing[key]);
      }
    }

    if (fields.length === 0) return false;

    values.push(id);
    const [res] = await pool.query(
      `UPDATE listings SET ${fields.join(', ')} WHERE id = ? AND deleted_at IS NULL`,
      values
    );
    return res.affectedRows > 0;
  },

  async softDelete(id) {
    const [res] = await pool.query(
      "UPDATE listings SET deleted_at = NOW(), status = 'archived' WHERE id = ? AND deleted_at IS NULL",
      [id]
    );
    return res.affectedRows > 0;
  },

  // Attributes
  async saveAttributes(listingId, attributes) {
    // Delete existing attributes
    await pool.query('DELETE FROM listing_attributes WHERE listing_id = ?', [listingId]);
    
    if (!attributes || attributes.length === 0) return;

    const queries = attributes.map(attr => 
      pool.query(
        'INSERT INTO listing_attributes (listing_id, attribute_name, attribute_value) VALUES (?, ?, ?)',
        [listingId, attr.name, attr.value]
      )
    );
    await Promise.all(queries);
  },

  // Images
  async addImage(listingId, imageUrl, sortOrder = 0, isPrimary = 0) {
    // If setting as primary, unset other primary images
    if (isPrimary === 1) {
      await pool.query('UPDATE listing_images SET is_primary = 0 WHERE listing_id = ?', [listingId]);
    }
    
    const [res] = await pool.query(
      'INSERT INTO listing_images (listing_id, image_url, sort_order, is_primary) VALUES (?, ?, ?, ?)',
      [listingId, imageUrl, sortOrder, isPrimary]
    );
    return res.insertId;
  },

  async deleteImage(listingId, imageId) {
    const [res] = await pool.query(
      'DELETE FROM listing_images WHERE id = ? AND listing_id = ?',
      [imageId, listingId]
    );
    return res.affectedRows > 0;
  },

  // Metrics (internal operations)
  async incrementViewCount(id) {
    await pool.query('UPDATE listings SET view_count = view_count + 1 WHERE id = ?', [id]);
  },

  async incrementBookingCount(id) {
    await pool.query('UPDATE listings SET booking_count = booking_count + 1 WHERE id = ?', [id]);
  },

  async updateListingRating(id) {
    // Calculate rating aggregates
    const [rows] = await pool.query(
      "SELECT COALESCE(AVG(rating), 0) as rating_avg, COUNT(*) as rating_cnt FROM reviews WHERE listing_id = ? AND status = 'approved'",
      [id]
    );
    const { rating_avg, rating_cnt } = rows[0];

    await pool.query(
      'UPDATE listings SET rating_average = ?, rating_count = ? WHERE id = ?',
      [Number(rating_avg).toFixed(2), rating_cnt, id]
    );
  }
};
