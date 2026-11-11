# Preventing SQL Injection in `mysql2/promise` (`sql-injection.md`)

SQL Injection (SQLi) occurs when malicious user input is concatenated directly into SQL queries, allowing attackers to manipulate queries, bypass login authentication, read unauthorized data, or delete entire database tables.

---

## 1. Vulnerable Code vs Secure Code

### Vulnerable Code (String Concatenation - DO NOT USE!)
```javascript
// DANGEROUS! If input email is "' OR '1'='1", authentication is bypassed!
const sql = `SELECT * FROM users WHERE email = '${req.body.email}' AND password = '${req.body.password}'`;
const [rows] = await pool.query(sql);
```

### Secure Code (Parameterized Queries - ALWAYS USE!)
```javascript
// SAFE! mysql2 escapes placeholders automatically.
const sql = 'SELECT * FROM users WHERE email = ? AND password = ?';
const [rows] = await pool.query(sql, [req.body.email, req.body.password]);
```

---

## 2. Dynamic Column and Table Name Security

Prepared statement placeholders (`?`) can only escape values (literals). They **cannot** be used for SQL identifiers like table or column names.

### Secure Handling for Dynamic Columns (Whitelisting):
```javascript
const allowedColumns = ['id', 'name', 'email', 'created_at'];

const sortColumn = req.query.sort;
if (!allowedColumns.includes(sortColumn)) {
  throw new Error('Invalid sort column identifier');
}

// Safe to concatenate ONLY after strict whitelisting check
const sql = `SELECT * FROM users ORDER BY ${sortColumn} ASC`;
const [rows] = await pool.query(sql);
```

---

## 3. Exam Rule Summary

> [!IMPORTANT]
> Always use `pool.query('SELECT ... WHERE field = ?', [value])` in BCA exam projects to ensure maximum marks and zero security vulnerabilities.
