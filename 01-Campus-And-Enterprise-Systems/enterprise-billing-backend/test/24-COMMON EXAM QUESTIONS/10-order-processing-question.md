# 10 - Order Processing & Status Exam Question

## QUESTION
Implement an Order Processing API that transitions orders between statuses (`pending` -> `processing` -> `completed` / `cancelled`). Validate status transitions and update inventory levels accordingly.

---

## REQUIREMENTS
- Endpoints:
  - `POST /api/orders` (Place order with status `pending`)
  - `PATCH /api/orders/:id/status` (Update order status)

---

## TABLES
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## FILES REQUIRED
1. `controllers/orderController.js`
2. `routes/orderRoutes.js`

---

## CODING ORDER
1. Setup `orders` table.
2. Build `updateOrderStatus` controller method.
3. If new status is `cancelled`, restore product stock levels.

---

## API FLOW
`PATCH /api/orders/1/status` Body: `{"status": "completed"}` -> Controller updates status -> Returns updated record.

---

## POSTMAN TEST
`PATCH http://localhost:5000/api/orders/1/status` Body: `{"status": "completed"}`

---

## COMMON MISTAKES
- Allowing invalid status values outside the ENUM array.
