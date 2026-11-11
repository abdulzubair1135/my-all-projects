# Final 30-Minute Pre-Exam Sprint Checklist

## ⏱️ Minutes 0–5: Project Setup
1. Open Terminal, navigate to project folder.
2. Initialize project: `npm init -y`
3. Edit `package.json` -> Add `"type": "module"`.
4. Install packages: `npm install express mysql2 dotenv bcrypt jsonwebtoken express-validator cors`
5. Create `.env` file with `PORT`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `JWT_SECRET`.

---

## ⏱️ Minutes 5–10: Database Setup
1. Start XAMPP/MySQL service.
2. Open MySQL CLI/phpMyAdmin -> Create database `CREATE DATABASE exam_db;`.
3. Create required tables with Primary Keys & Foreign Keys.
4. Insert 2–3 rows of sample testing data.

---

## ⏱️ Minutes 10–20: Code Construction
1. Create `config/db.js` using `mysql2/promise`.
2. Create `middleware/authMiddleware.js` for JWT authentication.
3. Create Controllers (`controllers/`) with `try...catch` blocks.
4. Create Routers (`routes/`) with parameter definitions.
5. Create `server.js` with `app.use(express.json())`, `app.use(cors())`, route mounting, and `app.listen()`.

---

## ⏱️ Minutes 20–30: Verification & Demo
1. Start server: `node server.js` -> Ensure `"Server running..."` logs cleanly.
2. Test Register -> Login -> Copy JWT.
3. Test CRUD endpoints in Postman.
4. Perform final error check before calling examiner for demo.
