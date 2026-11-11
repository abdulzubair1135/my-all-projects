import pool from '../config/db.js';

export const getAll = async () => {
  const [rows] = await pool.query('SELECT * FROM inventory_items ORDER BY id DESC');
  return rows;
};

export const getById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM inventory_items WHERE id = ?', [id]);
  return rows[0];
};

export const create = async (data) => {
  const { item_code, item_name, quantity, min_level, supplier } = data;
  const [result] = await pool.query(
    'INSERT INTO inventory_items (item_code, item_name, quantity, min_level, supplier) VALUES (?, ?, ?, ?, ?)',
    [item_code, item_name, quantity, min_level, supplier]
  );
  return result.insertId;
};

export const update = async (id, data) => {
  const { item_code, item_name, quantity, min_level, supplier } = data;
  const [result] = await pool.query(
    'UPDATE inventory_items SET item_code = ?, item_name = ?, quantity = ?, min_level = ?, supplier = ? WHERE id = ?',
    [item_code, item_name, quantity, min_level, supplier, id]
  );
  return result.affectedRows;
};

export const remove = async (id) => {
  const [result] = await pool.query('DELETE FROM inventory_items WHERE id = ?', [id]);
  return result.affectedRows;
};
