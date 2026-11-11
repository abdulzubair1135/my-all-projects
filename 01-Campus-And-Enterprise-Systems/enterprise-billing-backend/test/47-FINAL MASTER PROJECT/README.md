# 47 - Final Master Backend Project

A complete, production-ready, beginner-friendly Master Backend API built with **Express.js**, **MySQL (`mysql2/promise`)**, **MVC Architecture**, **Authentication (Bcrypt + JWT)**, **express-validator**, **Multer File Upload**, **SQL JOINs**, and **Database Transactions**.

---

## 🌟 Key Features

1. **ES Modules**: Pure ES Module imports/exports (`"type": "module"` in `package.json`).
2. **Database Integration**: Asynchronous MySQL pool using `mysql2/promise` with parameterized queries.
3. **Authentication & Authorization**: Password hashing with `bcryptjs`, JWT token verification, and Role-Based Access Control (Admin vs Customer).
4. **Input Validation**: Robust request validation and error messaging via `express-validator`.
5. **Multer Media Storage**: Image upload processing, file type filtering, size limiting, and static serving at `/uploads/`.
6. **SQL JOINs & Search/Pagination**: Fetching relational data across tables with page/limit offset pagination and keyword search filters.
7. **Database Transactions**: Atomic order checkout pipeline executing `beginTransaction`, `commit`, and `rollback`.
8. **Security Hardening**: Secure headers with `helmet`, CORS enablement, and SQL injection prevention.
9. **Standardized Responses**: Uniform JSON response helpers (`sendSuccess`, `sendError`).

---

## 📁 Directory Structure

```text
47-FINAL MASTER PROJECT/
├── config/
│   └── db.js                 # MySQL Pool Configuration
├── controllers/
│   ├── authController.js     # User registration, login, profile & avatar upload
│   ├── categoryController.js # Category CRUD operations
│   ├── productController.js  # Product catalog with search, pagination & image upload
│   └── orderController.js    # Checkout with DB transactions & order history
├── docs/
│   ├── api_endpoints.md      # API Route reference table
│   ├── architecture.md       # MVC & Layer flow explanation with Mermaid diagram
│   └── security.md           # Security & data integrity breakdown
├── middleware/
│   ├── authMiddleware.js     # JWT token verification & RBAC check
│   ├── errorHandler.js       # Centralized global error handling
│   └── uploadMiddleware.js   # Multer file upload setup
├── models/
│   ├── categoryModel.js     # Category DB queries
│   ├── orderModel.js        # Order DB transaction queries
│   ├── productModel.js      # Product JOIN & paginated DB queries
│   └── userModel.js         # User DB queries
├── Postman/
│   └── Master-API.json       # Postman Collection JSON (v2.1.0)
├── routes/
│   ├── authRoutes.js
│   ├── categoryRoutes.js
│   ├── orderRoutes.js
│   └── productRoutes.js
├── SQL/
│   └── schema.sql            # Master database table schema & seed data
├── utils/
│   └── response.js           # Standardized API response helpers
├── uploads/
│   └── .gitkeep              # Folder for user uploads
├── .env.example
├── package.json
├── README.md
└── server.js                 # Main Express Server Entrypoint
```

---

## 🚀 Quick Start Guide

### 1. Database Setup
Execute `SQL/schema.sql` in MySQL Workbench or phpMyAdmin:
```sql
SOURCE SQL/schema.sql;
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your MySQL credentials (`DB_USER`, `DB_PASS`, `DB_NAME`) match your local setup.

### 3. Install Dependencies & Run
```bash
npm install
npm run dev
```

---

## 🧪 Postman Collection Testing
Import `Postman/Master-API.json` into Postman to test all endpoints.
