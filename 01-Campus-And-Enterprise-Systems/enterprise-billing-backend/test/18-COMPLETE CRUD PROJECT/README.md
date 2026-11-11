# Complete CRUD Project (BCA Practical Exam)

A clean, production-standard, beginner-friendly REST API built with Node.js, Express, MySQL2 (`promise`), and `express-validator`.

---

## 🛠️ Tech Stack & Features
- **Node.js** with **ES Modules** (`"type": "module"`)
- **Express.js** for Routing
- **MySQL2** Connection Pool with Promise API (`mysql2/promise`)
- **express-validator** for request parameter & body validation
- Parameterized SQL queries to prevent SQL Injection (`?` placeholders)
- Standardized API Response format (`{ success, message, data/error }`)
- Global Error Handling Middleware

---

## 🚀 How to Run

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Setup MySQL Database:**
   - Run the SQL queries present in `SQL/users.sql` in phpMyAdmin or MySQL CLI:
   ```sql
   CREATE DATABASE crud_db;
   USE crud_db;
   -- execute rest of SQL/users.sql
   ```

3. **Configure Environment Variables:**
   - Create `.env` file or copy from `.env.example`:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=crud_db
   PORT=5000
   ```

4. **Start the Server:**
   ```bash
   npm start
   # or for auto-reload:
   npm run dev
   ```

---

## 📌 API Endpoints

| Method | Endpoint | Description | Sample Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health check endpoint | N/A |
| `GET` | `/api/users` | Fetch all users | N/A |
| `GET` | `/api/users/:id` | Fetch single user by ID | N/A |
| `POST` | `/api/users` | Create a new user | `{"name":"Aman","email":"aman@ex.com","age":24,"city":"Noida"}` |
| `PUT` | `/api/users/:id` | Update user details | `{"name":"Aman Sharma","email":"aman@ex.com","age":25,"city":"Delhi"}` |
| `DELETE`| `/api/users/:id` | Delete user by ID | N/A |
