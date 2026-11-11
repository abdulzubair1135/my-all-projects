import pool from '../config/database.js';

export const notificationRepository = {
  async create(userId, type, title, message, dataJson = null) {
    const dataString = dataJson ? JSON.stringify(dataJson) : null;
    const [res] = await pool.query(
      `INSERT INTO notifications (user_id, type, title, message, data_json, is_read)
       VALUES (?, ?, ?, ?, ?, 0)`,
      [userId, type, title, message, dataString]
    );
    return res.insertId;
  },

  async getUserNotifications(userId) {
    const [rows] = await pool.query(
      'SELECT id, user_id, type, title, message, data_json, is_read, created_at, read_at FROM notifications WHERE user_id = ? ORDER BY id DESC',
      [userId]
    );
    return rows.map(r => ({
      ...r,
      data_json: r.data_json ? JSON.parse(r.data_json) : null
    }));
  },

  async markAsRead(notificationId, userId) {
    const [res] = await pool.query(
      'UPDATE notifications SET is_read = 1, read_at = NOW() WHERE id = ? AND user_id = ?',
      [notificationId, userId]
    );
    return res.affectedRows > 0;
  },

  async markAllAsRead(userId) {
    await pool.query(
      'UPDATE notifications SET is_read = 1, read_at = NOW() WHERE user_id = ? AND is_read = 0',
      [userId]
    );
  }
};
