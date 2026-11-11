import pool from '../config/db.js';

export const createOrderTransaction = async (userId, shippingAddress, items) => {
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    let totalAmount = 0;
    const validatedItems = [];

    // Verify inventory stock & calculate subtotals
    for (const item of items) {
      const [productRows] = await connection.query(
        'SELECT id, title, price, stock FROM products WHERE id = ? FOR UPDATE',
        [item.product_id]
      );

      if (productRows.length === 0) {
        throw new Error(`Product ID ${item.product_id} not found.`);
      }

      const product = productRows[0];
      if (product.stock < item.quantity) {
        throw new Error(`Insufficient stock for product '${product.title}'. Requested: ${item.quantity}, Available: ${product.stock}`);
      }

      const subtotal = product.price * item.quantity;
      totalAmount += subtotal;

      validatedItems.push({
        product_id: product.id,
        quantity: item.quantity,
        unit_price: product.price,
        subtotal
      });
    }

    // Insert Order Master Header
    const [orderResult] = await connection.query(
      'INSERT INTO orders (user_id, total_amount, shipping_address, status) VALUES (?, ?, ?, ?)',
      [userId, totalAmount, shippingAddress, 'pending']
    );

    const orderId = orderResult.insertId;

    // Insert Order Detail Items & Deduct Stock
    for (const item of validatedItems) {
      await connection.query(
        'INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)',
        [orderId, item.product_id, item.quantity, item.unit_price, item.subtotal]
      );

      await connection.query(
        'UPDATE products SET stock = stock - ? WHERE id = ?',
        [item.quantity, item.product_id]
      );
    }

    await connection.commit();
    return { orderId, totalAmount, totalItems: validatedItems.length };
  } catch (error) {
    await connection.rollback();
    throw error;
  } finally {
    connection.release();
  }
};

export const getUserOrders = async (userId) => {
  const [rows] = await pool.query('SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC', [userId]);
  return rows;
};

export const getOrderByIdDetails = async (orderId, userId = null) => {
  let sql = 'SELECT * FROM orders WHERE id = ?';
  const params = [orderId];
  if (userId) {
    sql += ' AND user_id = ?';
    params.push(userId);
  }

  const [orders] = await pool.query(sql, params);
  if (orders.length === 0) return null;

  const itemsSql = `
    SELECT oi.id, oi.product_id, p.title AS product_title, p.image_url, oi.quantity, oi.unit_price, oi.subtotal
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.id
    WHERE oi.order_id = ?
  `;
  const [items] = await pool.query(itemsSql, [orderId]);

  return { ...orders[0], items };
};
