import pool from '../config/database.js';

export const bannerRepository = {
  async getActiveBanners() {
    const [rows] = await pool.query(
      `SELECT id, title, subtitle, image_url, action_type, action_value, priority 
       FROM banners 
       WHERE status = 'active' AND (start_at IS NULL OR start_at <= NOW()) AND (end_at IS NULL OR end_at >= NOW()) 
       ORDER BY priority ASC, id DESC`
    );
    return rows;
  },

  async create(banner) {
    const { title, subtitle, image_url, action_type, action_value, priority = 0, start_at = null, end_at = null, status = 'active' } = banner;
    const [res] = await pool.query(
      `INSERT INTO banners (title, subtitle, image_url, action_type, action_value, priority, start_at, end_at, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [title, subtitle, image_url, action_type, action_value, priority, start_at, end_at, status]
    );
    return res.insertId;
  },

  async update(id, banner) {
    const fields = [];
    const values = [];

    const allowed = ['title', 'subtitle', 'image_url', 'action_type', 'action_value', 'priority', 'start_at', 'end_at', 'status'];
    for (const key of allowed) {
      if (banner[key] !== undefined) {
        fields.push(`\`${key}\` = ?`);
        values.push(banner[key]);
      }
    }

    if (fields.length === 0) return false;

    values.push(id);
    const [res] = await pool.query(
      `UPDATE banners SET ${fields.join(', ')} WHERE id = ?`,
      values
    );
    return res.affectedRows > 0;
  },

  async delete(id) {
    const [res] = await pool.query('DELETE FROM banners WHERE id = ?', [id]);
    return res.affectedRows > 0;
  }
};
