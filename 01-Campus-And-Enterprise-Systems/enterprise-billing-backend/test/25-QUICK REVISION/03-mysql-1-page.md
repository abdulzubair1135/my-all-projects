# MySQL2 Promise One-Page Quick Revision Sheet

## Connection Pool Setup (`config/db.js`)
```javascript
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

export default pool;
```

---

## Standard Query Patterns

### 1. SELECT (Read)
```javascript
const [rows] = await pool.query('SELECT * FROM products WHERE category = ?', [category]);
```

### 2. INSERT (Create)
```javascript
const [result] = await pool.query(
    'INSERT INTO products (name, price) VALUES (?, ?)',
    [name, price]
);
console.log('Inserted ID:', result.insertId);
```

### 3. UPDATE / DELETE
```javascript
const [result] = await pool.query('UPDATE products SET price = ? WHERE id = ?', [price, id]);
console.log('Affected Rows:', result.affectedRows);
```

---

## MySQL Transactions Cheat Sheet
```javascript
const conn = await pool.getConnection();
try {
    await conn.beginTransaction();
    await conn.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
    await conn.query('UPDATE accounts SET balance = balance + 100 WHERE id = 2');
    await conn.commit();
} catch (error) {
    await conn.rollback();
    throw error;
} finally {
    conn.release();
}
```
