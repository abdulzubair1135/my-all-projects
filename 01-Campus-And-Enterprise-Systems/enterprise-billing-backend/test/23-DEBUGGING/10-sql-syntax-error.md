# 10 - SQL Syntax Error

## ERROR
`Error: ER_PARSE_ERROR: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near...`

---

## WHY IT HAPPENS
1. Typo in SQL keywords (`SELETC`, `INSERT INTOOO`, `WHERE` missing).
2. Mismatched dynamic placeholder count `?` versus parameterized array arguments `[val1, val2]`.
3. Trailing comma in SQL query or table definition (`id INT, name VARCHAR(100),`).

---

## HOW TO FIND IT
- MySQL error message specifies exact fragment of query near syntax error.
- Log SQL query string to console before execution: `console.log(sql, params)`.

---

## HOW TO FIX IT
1. Use parameterized queries safely with `mysql2/promise`:
```javascript
const sql = 'INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)';
const params = [name, category, price, stock];
const [result] = await pool.query(sql, params);
```
2. Double-check that argument array length matches `?` count:
```javascript
// Example check:
// 4 placeholders (?) -> array MUST have 4 items!
```

---

## COMMON EXAM MISTAKE
Using string interpolation like `` `SELECT * FROM users WHERE id = ${id}` `` instead of parameterized queries `pool.query('SELECT * FROM users WHERE id = ?', [id])`, exposing app to SQL Injection and syntax breaks on strings with quotes.
