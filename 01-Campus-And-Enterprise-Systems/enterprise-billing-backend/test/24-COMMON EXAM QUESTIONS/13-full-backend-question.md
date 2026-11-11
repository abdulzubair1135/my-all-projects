# 13 - Full Backend Comprehensive Exam Question

## QUESTION
Build a complete, production-ready Store Management REST API featuring User Auth (JWT/Bcrypt), Product CRUD, Customer Management, Billing with Transactions, and File Uploads, using MVC pattern in Express and MySQL.

---

## REQUIREMENTS
- Project must use ES Modules (`"type": "module"`).
- All endpoints must return standardized response structure (`success`, `message`, `data`/`error`).
- Database foreign key referential integrity enforced.
- Input validation on all POST/PUT routes using `express-validator`.

---

## TABLES
`users`, `products`, `customers`, `bills`, `bill_items`

---

## FILES REQUIRED
1. `.env`
2. `config/db.js`
3. `middleware/authMiddleware.js`
4. `middleware/validationMiddleware.js`
5. `controllers/authController.js`
6. `controllers/productController.js`
7. `controllers/billController.js`
8. `routes/authRoutes.js`
9. `routes/productRoutes.js`
10. `routes/billRoutes.js`
11. `server.js`

---

## CODING ORDER
1. Database Schema Execution (`schema.sql`).
2. Project Initialization (`package.json` -> `"type": "module"` -> dependencies).
3. Environment & DB Pool (`.env`, `db.js`).
4. Middlewares (Auth, Validation, CORS, Body-Parser).
5. Controllers & Routes module by module.
6. Server assembly (`server.js`) & Postman testing sequence.

---

## API FLOW
Auth (`/api/auth`) -> Products (`/api/products`) -> Bills (`/api/bills`) -> Standardized JSON.

---

## POSTMAN TEST
Full end-to-end collection execution covering Register, Login, Create Product, Create Customer, Generate Bill, and Fetch Analytics.

---

## COMMON MISTAKES
- Skipping input validation under exam time pressure, causing unhandled SQL errors on empty payloads.
