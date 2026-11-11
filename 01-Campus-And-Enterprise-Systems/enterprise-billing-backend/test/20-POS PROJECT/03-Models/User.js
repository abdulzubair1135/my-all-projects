/**
 * User Model for POS Application
 */

import pool from '../02-Config/db.js';

class User {
  static async findByEmail(email) {
    const sql = 'SELECT * FROM users WHERE email = ?';
    const [rows] = await pool.query(sql, [email]);
    return rows[0] || null;
  }

  static async findById(id) {
    const sql = 'SELECT id, name, email, role, created_at FROM users WHERE id = ?';
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  static async create({ name, email, password, role = 'cashier' }) {
    const sql = 'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)';
    const [result] = await pool.query(sql, [name, email, password, role]);
    return { id: result.insertId, name, email, role };
  }
}

export default User;
