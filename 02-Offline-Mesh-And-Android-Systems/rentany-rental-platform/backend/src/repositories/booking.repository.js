import pool from '../config/database.js';

export const bookingRepository = {
  // Queries that can accept an active transaction connection
  async findById(id) {
    const [rows] = await pool.query(
      `SELECT b.*, l.title as listing_title, l.location_address, l.city, l.latitude, l.longitude,
              li.image_url as listing_primary_image,
              renter.full_name as renter_name, renter.email as renter_email, renter.phone as renter_phone,
              owner.full_name as owner_name, owner.email as owner_email, owner.phone as owner_phone
       FROM bookings b
       JOIN listings l ON b.listing_id = l.id
       LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
       JOIN users renter ON b.renter_id = renter.id
       JOIN users owner ON b.owner_id = owner.id
       WHERE b.id = ?`,
      [id]
    );
    return rows[0] || null;
  },

  async findByUuid(uuid) {
    const [rows] = await pool.query(
      `SELECT b.*, l.title as listing_title, l.location_address, l.city, l.latitude, l.longitude,
              li.image_url as listing_primary_image,
              renter.full_name as renter_name, renter.email as renter_email, renter.phone as renter_phone,
              owner.full_name as owner_name, owner.email as owner_email, owner.phone as owner_phone
       FROM bookings b
       JOIN listings l ON b.listing_id = l.id
       LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
       JOIN users renter ON b.renter_id = renter.id
       JOIN users owner ON b.owner_id = owner.id
       WHERE b.uuid = ?`,
      [uuid]
    );
    return rows[0] || null;
  },

  async getOverlappingBookings(connection, listingId, startDate, endDate) {
    // Queries database for conflicting dates
    // Using FOR UPDATE on the bookings table
    const query = `
      SELECT id FROM bookings
      WHERE listing_id = ?
        AND booking_status IN ('pending', 'confirmed', 'active')
        AND (
          (start_date <= ? AND end_date >= ?)
          OR (start_date <= ? AND end_date >= ?)
          OR (start_date >= ? AND end_date <= ?)
        )
      FOR UPDATE
    `;
    const [rows] = await connection.query(query, [
      listingId, 
      startDate, startDate, 
      endDate, endDate, 
      startDate, endDate
    ]);
    return rows;
  },

  async lockListing(connection, listingId) {
    // Lock the listing row to prevent race conditions during booking
    const [rows] = await connection.query(
      'SELECT id, owner_id, title, price_per_day, refundable_deposit, status, quantity, minimum_rental_days, maximum_rental_days, delivery_available, delivery_fee FROM listings WHERE id = ? FOR UPDATE',
      [listingId]
    );
    return rows[0] || null;
  },

  async createBooking(connection, booking) {
    const {
      uuid, listing_id, renter_id, owner_id, start_date, end_date, rental_days,
      price_per_day, subtotal, delivery_fee = 0.00, service_fee = 0.00, discount = 0.00,
      deposit_amount = 0.00, total_amount, payment_status = 'pending', booking_status = 'pending'
    } = booking;

    const [res] = await connection.query(
      `INSERT INTO bookings (uuid, listing_id, renter_id, owner_id, start_date, end_date, rental_days,
        price_per_day, subtotal, delivery_fee, service_fee, discount, deposit_amount, total_amount,
        payment_status, booking_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [uuid, listing_id, renter_id, owner_id, start_date, end_date, rental_days,
        price_per_day, subtotal, delivery_fee, service_fee, discount, deposit_amount, total_amount,
        payment_status, booking_status]
    );
    return res.insertId;
  },

  async createBookingItemSnapshot(connection, itemId, snapshot) {
    const { booking_id, listing_id, listing_title, price_per_day, quantity, rental_days, subtotal } = snapshot;
    await connection.query(
      `INSERT INTO booking_items (booking_id, listing_id, listing_title, price_per_day, quantity, rental_days, subtotal)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [booking_id, listing_id, listing_title, price_per_day, quantity, rental_days, subtotal]
    );
  },

  async addAvailabilityBlock(connection, availability) {
    const { listing_id, start_date, end_date, status = 'booked', booking_id } = availability;
    await connection.query(
      `INSERT INTO listing_availability (listing_id, start_date, end_date, status, booking_id)
       VALUES (?, ?, ?, ?, ?)`,
      [listing_id, start_date, end_date, status, booking_id]
    );
  },

  async removeAvailabilityBlock(connection, bookingId) {
    await connection.query(
      'DELETE FROM listing_availability WHERE booking_id = ?',
      [bookingId]
    );
  },

  async updateBookingStatus(connection, id, statusData) {
    const fields = [];
    const values = [];
    
    const allowed = ['booking_status', 'payment_status', 'cancellation_reason', 'cancelled_by', 'cancelled_at', 'confirmed_at', 'started_at', 'returned_at', 'completed_at'];
    for (const key of allowed) {
      if (statusData[key] !== undefined) {
        fields.push(`\`${key}\` = ?`);
        values.push(statusData[key]);
      }
    }
    
    if (fields.length === 0) return false;
    
    values.push(id);
    const [res] = await connection.query(
      `UPDATE bookings SET ${fields.join(', ')} WHERE id = ?`,
      values
    );
    return res.affectedRows > 0;
  },

  async getUserBookings(userId, type = 'renter', filter = 'all') {
    let query = `
      SELECT b.*, l.title as listing_title, 
             li.image_url as listing_primary_image,
             renter.full_name as renter_name, owner.full_name as owner_name
      FROM bookings b
      JOIN listings l ON b.listing_id = l.id
      LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
      JOIN users renter ON b.renter_id = renter.id
      JOIN users owner ON b.owner_id = owner.id
      WHERE 1=1
    `;
    const params = [];

    // Filter by user role (renter or owner)
    if (type === 'owner') {
      query += ' AND b.owner_id = ?';
      params.push(userId);
    } else {
      query += ' AND b.renter_id = ?';
      params.push(userId);
    }

    // Filter by screen state (upcoming, ongoing, completed)
    const today = new Date().toISOString().split('T')[0];
    if (filter === 'upcoming') {
      query += " AND b.booking_status IN ('pending', 'confirmed') AND b.start_date > ?";
      params.push(today);
    } else if (filter === 'ongoing') {
      query += " AND b.booking_status = 'active'";
    } else if (filter === 'completed') {
      query += " AND b.booking_status IN ('completed', 'returned', 'cancelled', 'rejected')";
    }

    query += ' ORDER BY b.id DESC';
    const [rows] = await pool.query(query, params);
    return rows;
  },

  // Admin query features
  async getAllBookings({ limit = 20, offset = 0, status }) {
    let query = `
      SELECT b.*, l.title as listing_title, 
             renter.full_name as renter_name, owner.full_name as owner_name
      FROM bookings b
      JOIN listings l ON b.listing_id = l.id
      JOIN users renter ON b.renter_id = renter.id
      JOIN users owner ON b.owner_id = owner.id
      WHERE 1=1
    `;
    const params = [];

    if (status) {
      query += ' AND b.booking_status = ?';
      params.push(status);
    }

    query += ' ORDER BY b.id DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const [rows] = await pool.query(query, params);
    
    let countQuery = 'SELECT COUNT(*) as total FROM bookings WHERE 1=1';
    const countParams = [];
    if (status) {
      countQuery += ' AND booking_status = ?';
      countParams.push(status);
    }
    const [[{ total }]] = await pool.query(countQuery, countParams);

    return { bookings: rows, total };
  }
};
