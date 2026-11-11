import pool from '../config/db.js';

export const getProductsPaginated = async ({ search, category_id, page, limit }) => {
  const offset = (page - 1) * limit;
  let whereClause = 'WHERE 1=1';
  const params = [];

  if (search) {
    whereClause += ' AND (p.title LIKE ? OR p.description LIKE ?)';
    params.push(`%${search}%`, `%${search}%`);
  }

  if (category_id) {
    whereClause += ' AND p.category_id = ?';
    params.push(category_id);
  }

  // Count total matching items
  const countSql = `SELECT COUNT(*) AS total FROM products p ${whereClause}`;
  const [countRows] = await pool.query(countSql, params);
  const total = countRows[0].total;

  // SQL JOIN to include Category details
  const dataSql = `
    SELECT p.id, p.sku, p.title, p.description, p.price, p.stock, p.image_url, p.created_at,
           c.id AS category_id, c.category_name
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    ${whereClause}
    ORDER BY p.id DESC
    LIMIT ? OFFSET ?
  `;
  const [rows] = await pool.query(dataSql, [...params, limit, offset]);

  return {
    total,
    totalPages: Math.ceil(total / limit),
    currentPage: page,
    limit,
    products: rows
  };
};

export const getProductById = async (id) => {
  const sql = `
    SELECT p.id, p.sku, p.title, p.description, p.price, p.stock, p.image_url, p.created_at,
           c.id AS category_id, c.category_name
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    WHERE p.id = ?
  `;
  const [rows] = await pool.query(sql, [id]);
  return rows[0];
};

export const createProduct = async (productData) => {
  const { sku, title, description, price, stock, category_id, image_url } = productData;
  const [result] = await pool.query(
    'INSERT INTO products (sku, title, description, price, stock, category_id, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [sku, title, description, price, stock, category_id, image_url || null]
  );
  return result.insertId;
};

export const updateProduct = async (id, productData) => {
  const { sku, title, description, price, stock, category_id, image_url } = productData;
  const [result] = await pool.query(
    'UPDATE products SET sku = ?, title = ?, description = ?, price = ?, stock = ?, category_id = ?, image_url = COALESCE(?, image_url) WHERE id = ?',
    [sku, title, description, price, stock, category_id, image_url || null, id]
  );
  return result.affectedRows;
};

export const deleteProduct = async (id) => {
  const [result] = await pool.query('DELETE FROM products WHERE id = ?', [id]);
  return result.affectedRows;
};
