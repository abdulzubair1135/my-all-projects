# POS (Point of Sale) Multi-Entity REST API System

Complete multi-table production architecture backend project for Point of Sale system built for BCA Practical Exam.

---

## 🏗️ Folder Structure
- **01-Database:** Complete SQL DDL scripts (`schema.sql`, `users.sql`, `franchises.sql`, `products.sql`, `bills.sql`).
- **02-Config:** Database connection configuration pool (`db.js`).
- **03-Models:** Data Models (`User.js`, `Franchise.js`, `Product.js`, `Bill.js`).
- **04-Controllers:** Request controllers & business logic handlers (`auth.controller.js`, `franchise.controller.js`, `product.controller.js`, `bill.controller.js`).
- **05-Routes:** Express router definitions (`auth.routes.js`, `franchise.routes.js`, `product.routes.js`, `bill.routes.js`).
- **06-Middleware:** Authentication and Error middleware handlers (`auth.middleware.js`, `error.middleware.js`).
- **07-Validation:** Request payload validation rules using `express-validator`.
- **08-Server:** Central entry point script (`server.js`).
- **09-Postman:** Ready-to-import Postman Collection JSON (`POS-API.json`).

---

## ⚡ How to Run

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Setup Database:**
   Import `01-Database/schema.sql` into MySQL Server, followed by seed sample scripts (`users.sql`, `franchises.sql`, `products.sql`).

3. **Configure Environment:**
   Copy `.env.example` to `.env` and set MySQL credentials.

4. **Start Application:**
   ```bash
   npm start
   ```

---

## 📋 Key API Endpoints

| Method | Endpoint | Authorization | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | None | User/Cashier Login & Token Retrieval |
| `GET` | `/api/franchises` | None | List active store franchises |
| `POST` | `/api/franchises` | Bearer Token | Add new franchise store |
| `GET` | `/api/products` | None | Fetch catalog products (filter by franchise_id query) |
| `POST` | `/api/products` | Bearer Token | Add product to catalog |
| `POST` | `/api/bills` | Bearer Token | Calculate tax, deduct stock, and generate POS Invoice |
