# Database Relationships Guide

## Overview of Database Relationships

Database tables relate to each other in three main ways:

---

## 1. One-to-One (1:1)
Each record in Table A is related to exactly one record in Table B.

- **Example**: `users` and `user_profiles`.
- **Implementation**: Place a `UNIQUE` foreign key column in the child table.

```sql
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    bio TEXT,
    avatar_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 2. One-to-Many (1:N)
A single record in Table A can be associated with multiple records in Table B, but each record in Table B relates to only one record in Table A.

- **Example**: `customers` (1) to `bills` (Many). One customer can have multiple bills.
- **Implementation**: Add foreign key in the "Many" table pointing to the "One" table.

```sql
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

---

## 3. Many-to-Many (N:M)
Multiple records in Table A can relate to multiple records in Table B.

- **Example**: `franchises` and `products` (Inventory management). One franchise sells many products; one product is stocked in many franchises.
- **Implementation**: Requires a **Junction / Pivot Table** containing two Foreign Keys.

```sql
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    franchise_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 0,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY (franchise_id, product_id)
);
```

---

## Practical SQL Joins for Relationships

### INNER JOIN (Fetch bill details along with customer name)
```sql
SELECT 
    b.id AS bill_id,
    b.bill_number,
    c.name AS customer_name,
    c.phone,
    b.grand_total
FROM bills b
INNER JOIN customers c ON b.customer_id = c.id;
```
