// mysql-transaction.js
// Node.js MySQL Transaction Handler using mysql2/promise

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'test_db',
  waitForConnections: true,
  connectionLimit: 10
});

export const transferMoney = async (senderId, receiverId, amount) => {
  // 1. Get dedicated connection from pool for transaction isolation
  const connection = await pool.getConnection();

  try {
    // 2. Start transaction
    await connection.beginTransaction();

    // 3. Deduct from Sender
    const [senderResult] = await connection.query(
      'UPDATE bank_accounts SET balance = balance - ? WHERE id = ? AND balance >= ?',
      [amount, senderId, amount]
    );

    if (senderResult.affectedRows === 0) {
      throw new Error('Insufficient balance or sender account invalid');
    }

    // 4. Add to Receiver
    const [receiverResult] = await connection.query(
      'UPDATE bank_accounts SET balance = balance + ? WHERE id = ?',
      [amount, receiverId]
    );

    if (receiverResult.affectedRows === 0) {
      throw new Error('Receiver account invalid');
    }

    // 5. Commit transaction if all queries succeed
    await connection.commit();
    console.log(`Successfully transferred ₹${amount} from Account ${senderId} to Account ${receiverId}`);
    return { success: true, message: "Transfer completed successfully" };

  } catch (error) {
    // 6. Rollback transaction on any failure
    await connection.rollback();
    console.error("Transaction Failed. Changes rolled back.", error.message);
    return { success: false, message: "Transfer failed", error: error.message };
  } finally {
    // 7. Release connection back to pool
    connection.release();
  }
};
