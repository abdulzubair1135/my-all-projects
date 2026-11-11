# 03 - Billing System Exam Question

## QUESTION
Design a Billing & Invoice system that accepts a bill request with nested array of line items (`items: [{ product_id, quantity, unit_price }]`), calculates total, tax, and discount, creates header `bills` record and `bill_items` detail records inside a MySQL Transaction.

---

## REQUIREMENTS
- Support database transaction (`connection.beginTransaction()`, `connection.commit()`, `connection.rollback()`).
- Auto-generate unique bill number (e.g. `INV-2026-0001`).
- Deduct stock quantity in `products` table for purchased items.

---

## TABLES
```sql
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT DEFAULT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bill_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
);
```

---

## FILES REQUIRED
1. `config/db.js`
2. `controllers/billController.js`
3. `routes/billRoutes.js`
4. `server.js`

---

## CODING ORDER
1. Database tables setup.
2. `billController.js` -> Obtain connection from pool `const conn = await pool.getConnection()`.
3. Start transaction `await conn.beginTransaction()`.
4. Insert `bills` record -> get `bill_id = billResult.insertId`.
5. Loop through `items` array -> Insert `bill_items` & Update `products` stock.
6. Commit transaction `await conn.commit()`.

---

## API FLOW
`POST /api/bills` -> Start Transaction -> Insert Header -> Loop & Insert Items -> Update Stock -> Commit -> Return Invoice Summary.

---

## POSTMAN TEST
```json
POST http://localhost:5000/api/bills
{
  "customer_id": 1,
  "items": [
    { "product_id": 1, "quantity": 2, "unit_price": 499 },
    { "product_id": 2, "quantity": 1, "unit_price": 2499 }
  ]
}
```

---

## COMMON MISTAKES
- Not releasing DB connection in `finally` block (`conn.release()`).
- Forgetting `await conn.rollback()` inside `catch` block on errors.
