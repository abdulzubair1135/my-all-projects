# Authentication Project (BCA Practical Exam)

Complete JWT and Bcrypt user authentication system built with Node.js, Express, MySQL2, and express-validator.

---

## 🔑 Key Features
- **Password Hashing:** `bcrypt` with salt round factor of 10.
- **JWT Token Generation:** `jsonwebtoken` signed token with configurable expiration.
- **Protected Middleware:** Bearer header verification middleware (`authMiddleware`).
- **Validation:** `express-validator` check on register & login requests.

---

## 🗄️ SQL Table Schema

Execute in your MySQL database (`auth_db`):
```sql
CREATE DATABASE IF NOT EXISTS auth_db;
USE auth_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('user', 'admin') DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📌 API Endpoints

| Method | Endpoint | Authorization | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | None | Register new user account |
| `POST` | `/api/auth/login` | None | Authenticate user & return JWT token |
| `GET` | `/api/auth/me` | Bearer Token | Fetch current authenticated profile |
