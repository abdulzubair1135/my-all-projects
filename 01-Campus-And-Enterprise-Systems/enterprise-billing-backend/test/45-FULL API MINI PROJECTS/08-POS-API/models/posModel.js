import pool from '../config/db.js';

export const createOrderWithTransaction = async (customer_name, items) => {
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    let totalAmount = 0;
    const preparedItems = items.map(item => {
      const subtotal = item.unit_price * item.quantity;
      totalAmount += subtotal;
      return { ...item, subtotal };
    });

    const [orderResult] = await connection.query(
      'INSERT INTO orders (customer_name, total_amount) VALUES (?, ?)',
      [customer_name, totalAmount]
    );

    const orderId = orderResult.insertId;

    for (const item of preparedItems) {
      await connection.query(
        'INSERT INTO order_items (order_id, item_name, unit_price, quantity, subtotal) VALUES (?, ?, ?, ?, ?)',
        [orderId, item.item_name, item.unit_price, item.quantity, item.subtotal]
      );
    }

    await connection.commit();
    return { orderId, totalAmount, itemsCount: preparedItems.length };
  } catch (error) {
    await connection.rollback();
    throw error;
  } finally {
    connection.release();
  }
};

export const getAllOrders = async () => {
  const [rows] = await pool.query('SELECT * FROM orders ORDER BY id DESC');
  return rows;
};

export const getOrderDetails = async (orderId) => {
  const [orders] = await pool.query('SELECT * FROM orders WHERE id = ?', [orderId]);
  if (orders.length === 0) return null;

  const [items] = await pool.query('SELECT * FROM order_items WHERE order_id = ?', [orderId]);
  return { ...orders[0], items };
};
