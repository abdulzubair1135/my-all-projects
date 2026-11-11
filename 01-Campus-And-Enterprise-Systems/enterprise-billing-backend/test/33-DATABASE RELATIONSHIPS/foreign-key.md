# SQL Foreign Key Constraints Guide

## 1. What is a Foreign Key?
A Foreign Key is a field (or collection of fields) in one table that uniquely identifies a row of another table (or the same table). It establishes referential integrity between child and parent tables.

---

## 2. Benefits of Foreign Keys
- **Referential Integrity**: Prevents orphan records (e.g. inserting a student with non-existent `department_id`).
- **Data Consistency**: Ensures foreign key references match existing parent primary key values.
- **Automated Cascading**: Supports automatic deletion or updating of child records when parent record is updated/deleted.

---

## 3. Adding Foreign Keys in SQL

### Syntax during Table Creation:
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_orders_users 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);
```

### Syntax on Existing Table (ALTER TABLE):
```sql
ALTER TABLE orders
ADD CONSTRAINT fk_orders_users
FOREIGN KEY (user_id) REFERENCES users(id);
```
