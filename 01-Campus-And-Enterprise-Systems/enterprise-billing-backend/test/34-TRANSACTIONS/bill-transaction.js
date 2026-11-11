// bill-transaction.js
// Express Controller demonstrating E-Commerce Invoice Billing Transaction

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'test_db',
  waitForConnections: true
});

// POST /api/orders/create
export const createOrderBillingTransaction = async (req, res) => {
  const { customerId, items, totalAmount } = req.body;
  // items format: [{ productId: 1, quantity: 2, price: 500 }]

  const connection = await pool.getConnection();

  try {
    await connection.beginTransaction();

    // Step 1: Insert main order record
    const [orderResult] = await connection.query(
      'INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)',
      [customerId, totalAmount, 'COMPLETED']
    );
    const newOrderId = orderResult.insertId;

    // Step 2: Insert order items & reduce stock in loop
    for (const item of items) {
      // Check stock availability
      const [productRows] = await connection.query(
        'SELECT stock FROM products WHERE id = ? FOR UPDATE',
        [item.productId]
      );

      if (productRows.length === 0 || productRows[0].stock < item.quantity) {
        throw new Error(`Insufficient stock for product ID: ${item.productId}`);
      }

      // Deduct product stock
      await connection.query(
        'UPDATE products SET stock = stock - ? WHERE id = ?',
        [item.quantity, item.productId]
      );

      // Insert item line into order_items
      await connection.query(
        'INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)',
        [newOrderId, item.productId, item.quantity, item.price]
      );
    }

    // Step 3: Commit all queries together
    await connection.commit();

    return res.status(201).json({
      success: true,
      message: "Order placed successfully",
      data: { orderId: newOrderId, totalAmount }
    });

  } catch (error) {
    // Rollback changes on stock or order failure
    await connection.rollback();
    console.error("Order Transaction Error:", error.message);
    return res.status(500).json({
      success: false,
      message: "Order creation failed",
      error: error.message
    });
  } finally {
    connection.release();
  }
};
