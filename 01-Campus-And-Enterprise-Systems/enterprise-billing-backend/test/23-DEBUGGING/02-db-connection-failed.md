# 02 - Database Connection Failed

## ERROR
`Error: connect ECONNREFUSED 127.0.0.1:3306` or `Access denied for user 'root'@'localhost'`

---

## WHY IT HAPPENS
1. MySQL Service / XAMPP / WAMP is not running on the system.
2. Incorrect credentials in `.env` file (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`).
3. Specified database (`DB_NAME`) has not been created in MySQL.

---

## HOW TO FIND IT
- Inspect terminal error output when server tries to query DB.
- Look for `ER_BAD_DB_ERROR` or `ER_ACCESS_DENIED_ERROR`.

---

## HOW TO FIX IT
1. Ensure MySQL service / XAMPP Control Panel MySQL is started.
2. Open MySQL CLI or phpMyAdmin and create database:
```sql
CREATE DATABASE IF NOT EXISTS my_exam_db;
```
3. Verify your `.env` file configuration matches:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=rootpassword
DB_NAME=my_exam_db
DB_PORT=3306
```
4. Test connection using `pool.getConnection()` in `db.js`:
```javascript
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
dotenv.config();

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10
});

export default pool;
```

---

## COMMON EXAM MISTAKE
Forgetting to call `dotenv.config()` before attempting to access `process.env.DB_HOST`, causing variables to evaluate to `undefined`.
