/**
 * User Model
 * MySQL Database ke sath communication direct query parameters `?` se handle karta hai.
 * Prevent SQL Injection by parameterized queries.
 */

import pool from '../config/db.js';

class UserModel {
  // Fetch all users
  static async findAll() {
    const sql = 'SELECT * FROM users ORDER BY id DESC';
    const [rows] = await pool.query(sql);
    return rows;
  }

  // Fetch single user by ID
  static async findById(id) {
    const sql = 'SELECT * FROM users WHERE id = ?';
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  // Check if email exists
  static async findByEmail(email) {
    const sql = 'SELECT * FROM users WHERE email = ?';
    const [rows] = await pool.query(sql, [email]);
    return rows[0] || null;
  }

  // Insert new user
  static async create(userData) {
    const { name, email, age, city } = userData;
    const sql = 'INSERT INTO users (name, email, age, city) VALUES (?, ?, ?, ?)';
    const [result] = await pool.query(sql, [name, email, age, city]);
    return { id: result.insertId, ...userData };
  }

  // Update user by ID
  static async update(id, userData) {
    const { name, email, age, city } = userData;
    const sql = 'UPDATE users SET name = ?, email = ?, age = ?, city = ? WHERE id = ?';
    const [result] = await pool.query(sql, [name, email, age, city, id]);
    return result.affectedRows > 0;
  }

  // Delete user by ID
  static async delete(id) {
    const sql = 'DELETE FROM users WHERE id = ?';
    const [result] = await pool.query(sql, [id]);
    return result.affectedRows > 0;
  }
}

export default UserModel;
