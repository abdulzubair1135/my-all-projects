/**
 * Franchise Model for POS Application
 */

import pool from '../02-Config/db.js';

class Franchise {
  static async findAll() {
    const sql = 'SELECT * FROM franchises ORDER BY id DESC';
    const [rows] = await pool.query(sql);
    return rows;
  }

  static async findById(id) {
    const sql = 'SELECT * FROM franchises WHERE id = ?';
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  static async findByCode(code) {
    const sql = 'SELECT * FROM franchises WHERE code = ?';
    const [rows] = await pool.query(sql, [code]);
    return rows[0] || null;
  }

  static async create({ name, code, location, contact_number }) {
    const sql = 'INSERT INTO franchises (name, code, location, contact_number) VALUES (?, ?, ?, ?)';
    const [result] = await pool.query(sql, [name, code, location, contact_number]);
    return { id: result.insertId, name, code, location, contact_number };
  }
}

export default Franchise;
