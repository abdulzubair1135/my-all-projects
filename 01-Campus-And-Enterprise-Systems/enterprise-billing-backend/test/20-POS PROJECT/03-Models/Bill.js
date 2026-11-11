/**
 * Bill Model for POS Application
 */

import pool from '../02-Config/db.js';

class Bill {
  static async findAll() {
    const sql = `
      SELECT b.*, f.name as franchise_name, u.name as cashier_name 
      FROM bills b 
      JOIN franchises f ON b.franchise_id = f.id 
      JOIN users u ON b.user_id = u.id 
      ORDER BY b.id DESC
    `;
    const [rows] = await pool.query(sql);
    return rows;
  }

  static async findById(id) {
    const sql = `
      SELECT b.*, f.name as franchise_name, u.name as cashier_name 
      FROM bills b 
      JOIN franchises f ON b.franchise_id = f.id 
      JOIN users u ON b.user_id = u.id 
      WHERE b.id = ?
    `;
    const [rows] = await pool.query(sql, [id]);
    return rows[0] || null;
  }

  static async create(billData) {
    const {
      bill_number,
      franchise_id,
      user_id,
      customer_name,
      subtotal,
      tax_rate,
      tax_amount,
      grand_total,
      items
    } = billData;

    const sql = `
      INSERT INTO bills (bill_number, franchise_id, user_id, customer_name, subtotal, tax_rate, tax_amount, grand_total, items_json) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    const itemsJson = JSON.stringify(items);
    const [result] = await pool.query(sql, [
      bill_number,
      franchise_id,
      user_id,
      customer_name || 'Walk-in Customer',
      subtotal,
      tax_rate,
      tax_amount,
      grand_total,
      itemsJson
    ]);

    return { id: result.insertId, ...billData };
  }
}

export default Bill;
