/**
 * Product Model for POS Application
 */

import pool from '../02-Config/db.js';

class Product {
  static async findAll(franchise_id = null) {
    let sql = 'SELECT p.*, f.name as franchise_name FROM products p JOIN franchises f ON p.franchise_id = f.id';
    const params = [];
    if (franchise_id) {
      sql += ' WHERE p.franchise_id = ?';
      params.push(franchise_id);
    }
    sql += ' ORDER BY p.id DESC';
    const [rows] = await pool.query(sql, params);
    return rows;
  }

  static async findById(id) {
    const sql = 'SELECT * FROM products WHERE id = ?';
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  static async create({ franchise_id, name, category, price, stock }) {
    const sql = 'INSERT INTO products (franchise_id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)';
    const [result] = await pool.query(sql, [franchise_id, name, category, price, stock]);
    return { id: result.insertId, franchise_id, name, category, price, stock };
  }

  static async updateStock(id, newStock) {
    const sql = 'UPDATE products SET stock = ? WHERE id = ?';
    await pool.query(sql, [newStock, id]);
  }
}

export default Product;
