import pool from '../config/db.js';

export const getAll = async () => {
  const [rows] = await pool.query('SELECT * FROM products ORDER BY id DESC');
  return rows;
};

export const getById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM products WHERE id = ?', [id]);
  return rows[0];
};

export const create = async (data) => {
  const { sku, title, description, price, stock, category } = data;
  const [result] = await pool.query(
    'INSERT INTO products (sku, title, description, price, stock, category) VALUES (?, ?, ?, ?, ?, ?)',
    [sku, title, description, price, stock, category]
  );
  return result.insertId;
};

export const update = async (id, data) => {
  const { sku, title, description, price, stock, category } = data;
  const [result] = await pool.query(
    'UPDATE products SET sku = ?, title = ?, description = ?, price = ?, stock = ?, category = ? WHERE id = ?',
    [sku, title, description, price, stock, category, id]
  );
  return result.affectedRows;
};

export const remove = async (id) => {
  const [result] = await pool.query('DELETE FROM products WHERE id = ?', [id]);
  return result.affectedRows;
};
