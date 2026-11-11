/**
 * Auth User Model
 */

import pool from '../config/db.js';

class UserAuthModel {
  // Email se user search karna
  static async findByEmail(email) {
    const sql = 'SELECT * FROM users WHERE email = ?';
    const [rows] = await pool.query(sql, [email]);
    return rows[0] || null;
  }

  // ID se user search karna (without password)
  static async findById(id) {
    const sql = 'SELECT id, name, email, role, created_at FROM users WHERE id = ?';
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  // New user create / register karna
  static async create(userData) {
    const { name, email, password, role = 'user' } = userData;
    const sql = 'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)';
    const [result] = await pool.query(sql, [name, email, password, role]);
    return {
      id: result.insertId,
      name,
      email,
      role
    };
  }
}

export default UserAuthModel;
