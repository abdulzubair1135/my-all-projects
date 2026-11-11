import pool from '../config/db.js';

export const getAllCategories = async () => {
  const [rows] = await pool.query('SELECT * FROM categories ORDER BY category_name ASC');
  return rows;
};

export const getCategoryById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM categories WHERE id = ?', [id]);
  return rows[0];
};

export const createCategory = async (category_name, description) => {
  const [result] = await pool.query(
    'INSERT INTO categories (category_name, description) VALUES (?, ?)',
    [category_name, description]
  );
  return result.insertId;
};

export const updateCategory = async (id, category_name, description) => {
  const [result] = await pool.query(
    'UPDATE categories SET category_name = ?, description = ? WHERE id = ?',
    [category_name, description, id]
  );
  return result.affectedRows;
};

export const deleteCategory = async (id) => {
  const [result] = await pool.query('DELETE FROM categories WHERE id = ?', [id]);
  return result.affectedRows;
};
