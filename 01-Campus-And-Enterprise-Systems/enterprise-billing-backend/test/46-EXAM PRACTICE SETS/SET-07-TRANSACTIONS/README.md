# SET 07 - MySQL Database Transactions

## Question
Write a bank fund transfer API endpoint in Express.js using MySQL transactions (`beginTransaction`, `commit`, `rollback`).

---

## Requirements
1. Endpoint `POST /api/bank/transfer`:
   - Inputs: `sender_id`, `receiver_id`, `amount`.
2. Steps:
   - Check if sender has sufficient balance.
   - Deduct `amount` from sender's balance.
   - Add `amount` to receiver's balance.
   - Log transaction entry in `transfer_logs` table.
3. If any step fails, call `rollback()` and revert changes.

---

## Solution Code

### `controllers/bankController.js`
```javascript
import pool from '../config/db.js';

export const transferFunds = async (req, res, next) => {
  const connection = await pool.getConnection();
  try {
    const { sender_id, receiver_id, amount } = req.body;

    await connection.beginTransaction();

    // 1. Check Sender Balance
    const [senderRows] = await connection.query('SELECT balance FROM accounts WHERE id = ? FOR UPDATE', [sender_id]);
    if (senderRows.length === 0 || senderRows[0].balance < amount) {
      throw new Error('Insufficient balance or invalid sender account');
    }

    // 2. Deduct from Sender
    await connection.query('UPDATE accounts SET balance = balance - ? WHERE id = ?', [amount, sender_id]);

    // 3. Add to Receiver
    await connection.query('UPDATE accounts SET balance = balance + ? WHERE id = ?', [amount, receiver_id]);

    // 4. Log Transfer
    await connection.query(
      'INSERT INTO transfer_logs (sender_id, receiver_id, amount) VALUES (?, ?, ?)',
      [sender_id, receiver_id, amount]
    );

    await connection.commit();
    res.json({ success: true, message: 'Transfer completed successfully' });
  } catch (err) {
    await connection.rollback();
    res.status(400).json({ success: false, message: 'Transfer failed', error: err.message });
  } finally {
    connection.release();
  }
};
```
