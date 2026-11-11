# SET 04 - Relational Queries & SQL JOINs

## Question
Build an Express API endpoint that fetches all **Orders** along with their **Customer Name** and **Product Details** using SQL `INNER JOIN`.

---

## Requirements
1. DB Tables:
   - `customers`: `id`, `name`, `email`
   - `orders`: `id`, `customer_id`, `product_name`, `amount`, `order_date`
2. Endpoint `GET /api/orders/details` must perform `INNER JOIN` to map `customer_id` to `customers.name`.

---

## Hints
- `SELECT orders.id, customers.name AS customer_name, orders.product_name, orders.amount FROM orders INNER JOIN customers ON orders.customer_id = customers.id`

---

## Solution Code

### `models/orderModel.js`
```javascript
import pool from '../config/db.js';

export const getOrderDetails = async () => {
  const sql = `
    SELECT 
      o.id AS order_id, 
      c.name AS customer_name, 
      c.email AS customer_email, 
      o.product_name, 
      o.amount, 
      o.order_date
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    ORDER BY o.id DESC
  `;
  const [rows] = await pool.query(sql);
  return rows;
};
```

---

## Postman Test Guide
- Send `GET http://localhost:5000/api/orders/details` to inspect joined fields.
