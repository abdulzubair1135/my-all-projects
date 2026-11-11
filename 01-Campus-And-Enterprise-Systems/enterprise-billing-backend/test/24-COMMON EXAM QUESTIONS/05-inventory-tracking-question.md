# 05 - Inventory Tracking Exam Question

## QUESTION
Create an Inventory Tracking API that tracks stock levels across franchises. Implement stock transfer between franchises and alert low-stock items (`quantity < min_threshold`).

---

## REQUIREMENTS
- Endpoints:
  - `GET /api/inventory/low-stock` (Get items below threshold)
  - `POST /api/inventory/transfer` (Transfer quantity from Franchise A to Franchise B using MySQL Transaction)

---

## TABLES
```sql
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    franchise_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    min_threshold INT NOT NULL DEFAULT 5,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

---

## FILES REQUIRED
1. `config/db.js`
2. `controllers/inventoryController.js`
3. `routes/inventoryRoutes.js`
4. `server.js`

---

## CODING ORDER
1. Schema & FK Setup.
2. Low Stock query (`WHERE quantity <= min_threshold`).
3. Stock transfer transaction logic (`UPDATE inventory SET quantity = quantity - ? WHERE franchise_id = ?` and `UPDATE inventory SET quantity = quantity + ? WHERE franchise_id = ?`).

---

## API FLOW
`POST /api/inventory/transfer` -> Check source stock -> Begin Tx -> Deduct Source -> Add Destination -> Commit.

---

## POSTMAN TEST
`POST http://localhost:5000/api/inventory/transfer` Body: `{"from_franchise_id": 1, "to_franchise_id": 2, "product_id": 1, "qty": 5}`

---

## COMMON MISTAKES
- Deducting stock without checking if `quantity >= requested_transfer_qty`.
