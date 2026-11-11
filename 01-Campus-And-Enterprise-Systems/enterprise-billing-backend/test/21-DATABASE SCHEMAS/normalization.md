# Database Normalization Guide (1NF, 2NF, 3NF)

## What is Normalization?
**Normalization** is a database design technique that organizes tables to reduce data redundancy and eliminate anomalies during INSERT, UPDATE, and DELETE operations.

---

## 1. First Normal Form (1NF) - Atomic Values
- **Rule**: Each column must contain atomic (indivisible) values, and there must be no repeating groups or comma-separated lists in a single field.
- **Violation Example**: `items = "Mouse, Keyboard, Monitor"` in one column.
- **Correction**: Split items into separate rows or separate child table (`bill_items`).

---

## 2. Second Normal Form (2NF) - Full Functional Dependency
- **Rule**: Must be in 1NF AND all non-key attributes must depend on the **entire** Primary Key (applies mainly to composite keys).
- **Violation Example**: In a table with composite key `(order_id, product_id)`, storing `product_name` in the same table. `product_name` depends only on `product_id`, not `order_id`.
- **Correction**: Move `product_name` to a separate `products` table.

---

## 3. Third Normal Form (3NF) - No Transitive Dependency
- **Rule**: Must be in 2NF AND non-key columns must NOT depend on other non-key columns.
- **Violation Example**: Storing `customer_city` and `customer_pincode` in `bills` table where `customer_city` depends on `customer_pincode`.
- **Correction**: Keep customer information strictly inside the `customers` table and reference only `customer_id` in `bills`.

---

## Summary Cheat Table

| Normal Form | Key Requirement | Quick Exam Answer |
| :--- | :--- | :--- |
| **1NF** | Atomic Values | No multi-value or comma-separated columns |
| **2NF** | In 1NF + No Partial Dependency | Non-key columns depend on full composite PK |
| **3NF** | In 2NF + No Transitive Dependency | Non-key columns depend only on Primary Key |
