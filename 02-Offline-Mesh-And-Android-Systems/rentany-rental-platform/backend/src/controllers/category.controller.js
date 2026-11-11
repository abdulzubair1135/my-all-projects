import pool from '../config/database.js';
import { AppError } from '../middleware/error.middleware.js';

export const categoryController = {
  async getCategories(req, res, next) {
    try {
      const [rows] = await pool.query(
        "SELECT id, name, slug, description, icon, image, parent_id, status FROM categories WHERE status = 'active' ORDER BY name ASC"
      );
      res.status(200).json({
        success: true,
        data: rows
      });
    } catch (err) {
      next(err);
    }
  },

  async getCategory(req, res, next) {
    try {
      const id = Number(req.params.id);
      const [rows] = await pool.query(
        "SELECT id, name, slug, description, icon, image, parent_id, status FROM categories WHERE id = ?",
        [id]
      );

      if (rows.length === 0) {
        throw new AppError('Category not found.', 404);
      }

      res.status(200).json({
        success: true,
        data: rows[0]
      });
    } catch (err) {
      next(err);
    }
  },

  async getCategoryListings(req, res, next) {
    try {
      const id = Number(req.params.id);
      const [listings] = await pool.query(
        `SELECT l.*, c.name as category_name, li.image_url as listing_primary_image
         FROM listings l
         JOIN categories c ON l.category_id = c.id
         LEFT JOIN listing_images li ON l.id = li.listing_id AND li.is_primary = 1
         WHERE l.category_id = ? AND l.status = 'published' AND l.deleted_at IS NULL
         ORDER BY l.id DESC`,
        [id]
      );

      res.status(200).json({
        success: true,
        data: listings
      });
    } catch (err) {
      next(err);
    }
  },

  // Admin Features
  async createCategory(req, res, next) {
    try {
      const { name, slug, description, icon, image, parent_id } = req.body;

      // Check slug uniqueness
      const [existing] = await pool.query('SELECT 1 FROM categories WHERE slug = ?', [slug]);
      if (existing.length > 0) {
        throw new AppError('Category slug is already in use.', 400);
      }

      const [insertRes] = await pool.query(
        `INSERT INTO categories (name, slug, description, icon, image, parent_id, status)
         VALUES (?, ?, ?, ?, ?, ?, 'active')`,
        [name, slug, description, icon, image, parent_id || null]
      );

      const [newCat] = await pool.query('SELECT * FROM categories WHERE id = ?', [insertRes.insertId]);

      res.status(201).json({
        success: true,
        message: 'Category created successfully',
        data: newCat[0]
      });
    } catch (err) {
      next(err);
    }
  },

  async updateCategory(req, res, next) {
    try {
      const id = Number(req.params.id);
      const { name, slug, description, icon, image, parent_id, status } = req.body;

      // Check if category exists
      const [cat] = await pool.query('SELECT 1 FROM categories WHERE id = ?', [id]);
      if (cat.length === 0) {
        throw new AppError('Category not found.', 404);
      }

      // Check slug uniqueness if modified
      if (slug) {
        const [existing] = await pool.query('SELECT id FROM categories WHERE slug = ? AND id != ?', [slug, id]);
        if (existing.length > 0) {
          throw new AppError('Category slug is already in use.', 400);
        }
      }

      const fields = [];
      const values = [];
      const allowed = ['name', 'slug', 'description', 'icon', 'image', 'parent_id', 'status'];
      for (const key of allowed) {
        if (req.body[key] !== undefined) {
          fields.push(`\`${key}\` = ?`);
          values.push(req.body[key]);
        }
      }

      if (fields.length > 0) {
        values.push(id);
        await pool.query(`UPDATE categories SET ${fields.join(', ')} WHERE id = ?`, values);
      }

      const [updatedCat] = await pool.query('SELECT * FROM categories WHERE id = ?', [id]);

      res.status(200).json({
        success: true,
        message: 'Category updated successfully',
        data: updatedCat[0]
      });
    } catch (err) {
      next(err);
    }
  },

  async deleteCategory(req, res, next) {
    try {
      const id = Number(req.params.id);
      const [cat] = await pool.query('SELECT 1 FROM categories WHERE id = ?', [id]);
      if (cat.length === 0) {
        throw new AppError('Category not found.', 404);
      }

      // Instead of hard deleting, we can deactivate it so active listings remain intact
      await pool.query("UPDATE categories SET status = 'inactive' WHERE id = ?", [id]);

      res.status(200).json({
        success: true,
        message: 'Category deactivated successfully'
      });
    } catch (err) {
      next(err);
    }
  }
};
