import pool from '../config/db.js';

export const getAll = async () => {
  const [rows] = await pool.query('SELECT * FROM posts ORDER BY id DESC');
  return rows;
};

export const getById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM posts WHERE id = ?', [id]);
  return rows[0];
};

export const create = async (data) => {
  const { title, slug, content, author_name, status } = data;
  const [result] = await pool.query(
    'INSERT INTO posts (title, slug, content, author_name, status) VALUES (?, ?, ?, ?, ?)',
    [title, slug, content, author_name, status || 'draft']
  );
  return result.insertId;
};

export const update = async (id, data) => {
  const { title, slug, content, author_name, status } = data;
  const [result] = await pool.query(
    'UPDATE posts SET title = ?, slug = ?, content = ?, author_name = ?, status = ? WHERE id = ?',
    [title, slug, content, author_name, status, id]
  );
  return result.affectedRows;
};

export const remove = async (id) => {
  const [result] = await pool.query('DELETE FROM posts WHERE id = ?', [id]);
  return result.affectedRows;
};
