import pool from '../config/database.js';

export const userRepository = {
  async findById(id) {
    const [rows] = await pool.query(
      'SELECT id, uuid, full_name, email, phone, password_hash, profile_image, role, status, email_verified, phone_verified, created_at, updated_at, last_login_at FROM users WHERE id = ?',
      [id]
    );
    return rows[0] || null;
  },

  async findByUuid(uuid) {
    const [rows] = await pool.query(
      'SELECT id, uuid, full_name, email, phone, password_hash, profile_image, role, status, email_verified, phone_verified, created_at, updated_at, last_login_at FROM users WHERE uuid = ?',
      [uuid]
    );
    return rows[0] || null;
  },

  async findByEmail(email) {
    const [rows] = await pool.query(
      'SELECT id, uuid, full_name, email, phone, password_hash, profile_image, role, status, email_verified, phone_verified, created_at, updated_at, last_login_at FROM users WHERE email = ?',
      [email]
    );
    return rows[0] || null;
  },

  async findByPhone(phone) {
    const [rows] = await pool.query(
      'SELECT id, uuid, full_name, email, phone, password_hash, profile_image, role, status, email_verified, phone_verified, created_at, updated_at, last_login_at FROM users WHERE phone = ?',
      [phone]
    );
    return rows[0] || null;
  },

  async create(user) {
    const { uuid, full_name, email, phone, password_hash, role = 'user' } = user;
    const [res] = await pool.query(
      `INSERT INTO users (uuid, full_name, email, phone, password_hash, role, status, email_verified, phone_verified)
       VALUES (?, ?, ?, ?, ?, ?, 'active', 0, 0)`,
      [uuid, full_name, email, phone, password_hash, role]
    );
    return res.insertId;
  },

  async update(id, data) {
    const fields = [];
    const values = [];
    
    // Whitelist allowed fields to update
    const allowed = ['full_name', 'email', 'phone', 'profile_image', 'status', 'role', 'email_verified', 'phone_verified'];
    for (const key of allowed) {
      if (data[key] !== undefined) {
        fields.push(`\`${key}\` = ?`);
        values.push(data[key]);
      }
    }
    
    if (fields.length === 0) return false;
    
    values.push(id);
    const [res] = await pool.query(
      `UPDATE users SET ${fields.join(', ')} WHERE id = ?`,
      values
    );
    return res.affectedRows > 0;
  },

  async updateLastLogin(id) {
    await pool.query('UPDATE users SET last_login_at = NOW() WHERE id = ?', [id]);
  },

  // User addresses management
  async getAddresses(userId) {
    const [rows] = await pool.query(
      'SELECT id, user_id, address_line, city, state, country, postal_code, latitude, longitude, is_default, created_at FROM user_addresses WHERE user_id = ? ORDER BY is_default DESC, id DESC',
      [userId]
    );
    return rows;
  },

  async createAddress(userId, address) {
    const { address_line, city, state, country, postal_code, latitude, longitude, is_default = 0 } = address;
    
    // If setting as default, unset previous default addresses
    if (is_default === 1) {
      await pool.query('UPDATE user_addresses SET is_default = 0 WHERE user_id = ?', [userId]);
    }

    const [res] = await pool.query(
      `INSERT INTO user_addresses (user_id, address_line, city, state, country, postal_code, latitude, longitude, is_default)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [userId, address_line, city, state, country, postal_code, latitude, longitude, is_default]
    );
    return res.insertId;
  },

  async deleteAddress(addressId, userId) {
    const [res] = await pool.query(
      'DELETE FROM user_addresses WHERE id = ? AND user_id = ?',
      [addressId, userId]
    );
    return res.affectedRows > 0;
  },

  async setDefaultAddress(addressId, userId) {
    // 1. Unset all defaults
    await pool.query('UPDATE user_addresses SET is_default = 0 WHERE user_id = ?', [userId]);
    // 2. Set current default
    const [res] = await pool.query(
      'UPDATE user_addresses SET is_default = 1 WHERE id = ? AND user_id = ?',
      [addressId, userId]
    );
    return res.affectedRows > 0;
  },

  // Admin query features
  async getAllUsers({ limit = 20, offset = 0, status, search }) {
    let query = 'SELECT id, uuid, full_name, email, phone, role, status, email_verified, phone_verified, created_at, last_login_at FROM users WHERE 1=1';
    const params = [];

    if (status) {
      query += ' AND status = ?';
      params.push(status);
    }

    if (search) {
      query += ' AND (full_name LIKE ? OR email LIKE ? OR phone LIKE ?)';
      const s = `%${search}%`;
      params.push(s, s, s);
    }

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const [rows] = await pool.query(query, params);
    
    // Get total count
    let countQuery = 'SELECT COUNT(*) as total FROM users WHERE 1=1';
    const countParams = [];
    if (status) {
      countQuery += ' AND status = ?';
      countParams.push(status);
    }
    if (search) {
      countQuery += ' AND (full_name LIKE ? OR email LIKE ? OR phone LIKE ?)';
      const s = `%${search}%`;
      countParams.push(s, s, s);
    }
    const [[{ total }]] = await pool.query(countQuery, countParams);

    return { users: rows, total };
  }
};
