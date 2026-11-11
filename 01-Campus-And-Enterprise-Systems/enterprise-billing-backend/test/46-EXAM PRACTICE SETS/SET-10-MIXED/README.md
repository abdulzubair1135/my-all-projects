# SET 10 - Master Exam Mixed Problem

## Question
Design a full E-Commerce Backend System featuring:
1. User Authentication (Bcrypt + JWT + Role-based permissions).
2. Product Catalog with Multer image upload, Search filter & Pagination.
3. Category management with SQL JOIN queries.
4. Checkout System using MySQL Transactions (`beginTransaction`, `commit`, `rollback`).
5. Centralized Error Handler & express-validator input sanitization.

---

## Complete Solution Checklist
- [x] ES Modules (`"type": "module"` in `package.json`)
- [x] Connection Pool with `mysql2/promise`
- [x] Structured MVC Architecture (`config`, `models`, `controllers`, `routes`, `middleware`, `validation`, `utils`)
- [x] Express Validator rules on register, product creation & checkout
- [x] Password hashing with `bcryptjs`
- [x] Security headers (`helmet`) & CORS support
- [x] File upload via `multer` serving static files on `/uploads/`
- [x] SQL Joins for fetching Product + Category details
- [x] DB Transactions for Order placement
