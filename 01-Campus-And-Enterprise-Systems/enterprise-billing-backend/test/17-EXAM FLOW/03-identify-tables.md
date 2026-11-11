# Step 03: Identify Tables & Relationships

Database design examiner maximum marks carry karta hai. Is steps me entities analyze karke SQL Schema identify karte hain.

---

## 1. Simple Entity Mapping

### Project 1: User / CRUD Project
- **Table:** `users`
  - `id` (INT, Primary Key, Auto Increment)
  - `name` (VARCHAR 100, NOT NULL)
  - `email` (VARCHAR 100, UNIQUE, NOT NULL)
  - `password` (VARCHAR 255, NOT NULL)
  - `role` (ENUM('admin', 'user'), DEFAULT 'user')
  - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---

### Project 2: POS (Point of Sale) Multi-Table System
- **Table 1:** `users` (Cashiers / Admins)
- **Table 2:** `franchises` (Stores / Branches)
  - `id` (INT, PK, AI)
  - `name` (VARCHAR 100)
  - `location` (VARCHAR 255)
  - `code` (VARCHAR 20, UNIQUE)
- **Table 3:** `products` (Items)
  - `id` (INT, PK, AI)
  - `franchise_id` (INT, FK -> franchises.id)
  - `name` (VARCHAR 100)
  - `price` (DECIMAL 10,2)
  - `stock` (INT)
- **Table 4:** `bills` (Sales / Orders)
  - `id` (INT, PK, AI)
  - `bill_number` (VARCHAR 50, UNIQUE)
  - `franchise_id` (INT, FK -> franchises.id)
  - `user_id` (INT, FK -> users.id)
  - `total_amount` (DECIMAL 10,2)
  - `tax_amount` (DECIMAL 10,2)
  - `grand_total` (DECIMAL 10,2)
  - `created_at` (TIMESTAMP)

---

## 2. Foreign Key Diagram (POS System)
```
users (1) ------< (N) bills (N) >------ (1) franchises (1) ------< (N) products
```
