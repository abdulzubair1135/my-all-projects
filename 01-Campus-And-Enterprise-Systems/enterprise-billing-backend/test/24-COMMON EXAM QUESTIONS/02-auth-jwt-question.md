# 02 - User Auth & JWT Exam Question

## QUESTION
Develop a User Authentication system with User Registration, Login (password hashing with bcrypt), JWT token generation, and a protected `/api/users/profile` endpoint.

---

## REQUIREMENTS
- Database table `users` with `id`, `name`, `email`, `password`, `role`.
- `POST /api/auth/register` (Validate email/password, hash password with `bcrypt.hash`, save user).
- `POST /api/auth/login` (Verify password with `bcrypt.compare`, sign JWT with `jwt.sign`).
- `GET /api/users/profile` (Protected route using JWT Auth Middleware).

---

## TABLES
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## FILES REQUIRED
1. `config/db.js`
2. `controllers/authController.js`
3. `middleware/authMiddleware.js`
4. `routes/authRoutes.js`
5. `routes/userRoutes.js`
6. `server.js`

---

## CODING ORDER
1. Database setup -> Table `users`.
2. Environment configuration `.env` -> `JWT_SECRET=myexamsecret`.
3. `authController.js` (register & login logic).
4. `authMiddleware.js` (verify Bearer token).
5. Router setup & integration in `server.js`.

---

## API FLOW
1. **Register**: `POST /api/auth/register` -> Hash password -> `INSERT INTO users` -> Return status 201.
2. **Login**: `POST /api/auth/login` -> Fetch user -> Compare bcrypt hash -> Generate JWT token -> Return token.
3. **Profile**: `GET /api/users/profile` -> Auth Middleware verifies header `Authorization: Bearer <token>` -> Controller returns `req.user`.

---

## POSTMAN TEST
- Register: `POST /api/auth/register` with `{"name": "Admin", "email": "a@a.com", "password": "123"}`
- Login: `POST /api/auth/login` with `{"email": "a@a.com", "password": "123"}` -> Copy `token`
- Profile: `GET /api/users/profile` Header `Authorization: Bearer <token>`

---

## COMMON MISTAKES
- Storing plain text password in database.
- Forgetting `Bearer ` prefix stripping in `authMiddleware.js` (`authHeader.split(' ')[1]`).
