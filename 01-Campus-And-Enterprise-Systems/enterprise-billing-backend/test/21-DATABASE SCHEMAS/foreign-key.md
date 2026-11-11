# Foreign Key & Referential Integrity Guide

## What is a Foreign Key?
A **Foreign Key (FK)** is a field (or collection of fields) in one table that refers to the **Primary Key (PK)** in another table. It establishes and enforces a link between the data in the two tables, preserving **Referential Integrity**.

---

## Key Foreign Key Actions (`ON DELETE` / `ON UPDATE`)

1. **`ON DELETE CASCADE`**:
   - If the referenced row in the parent table is deleted, all matching child rows are automatically deleted.
   - *Example*: Deleting a bill deletes all associated `bill_items`.

2. **`ON DELETE SET NULL`**:
   - If the parent record is deleted, the FK column in child rows is set to `NULL`.
   - *Example*: Deleting a customer keeps the invoice record, but sets `customer_id = NULL`.

3. **`ON DELETE RESTRICT` / `NO ACTION`** (Default):
   - Prevents deletion of the parent record if child records exist.
   - *Example*: Prevents deleting a product if it has existing bills.

---

## SQL Code Syntax Example

```sql
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT DEFAULT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE TABLE bill_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);
```

---

## Exam Tips & Common Mistakes
- **Type Matching**: The data type of the Foreign Key column MUST match the target Primary Key column exactly (e.g., `INT` with `INT`, `UNSIGNED` with `UNSIGNED`).
- **Parent Insertion Order**: When populating tables with sample data in MySQL scripts, create and populate the **Parent Table** *before* the **Child Table**.
- **InnoDB Engine**: MySQL foreign key constraints only work with `ENGINE=InnoDB`.
