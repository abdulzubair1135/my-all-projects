import pool from '../config/db.js';

export const findByEmail = async (email) => {
  const [rows] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
  return rows[0];
};

export const findById = async (id) => {
  const [rows] = await pool.query('SELECT id, name, email, role, avatar, created_at FROM users WHERE id = ?', [id]);
  return rows[0];
};

export const createUser = async (name, email, hashedPassword, role = 'customer') => {
  const [result] = await pool.query(
    'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
    [name, email, hashedPassword, role]
  );
  return result.insertId;
};

export const updateAvatar = async (userId, avatarPath) => {
  const [result] = await pool.query('UPDATE users SET avatar = ? WHERE id = ?', [avatarPath, userId]);
  return result.affectedRows;
};
