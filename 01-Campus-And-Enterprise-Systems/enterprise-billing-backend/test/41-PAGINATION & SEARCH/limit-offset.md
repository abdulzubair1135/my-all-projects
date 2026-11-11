# SQL LIMIT and OFFSET Guide with `mysql2/promise` (`limit-offset.md`)

MySQL uses the `LIMIT` and `OFFSET` clauses to retrieve a specific slice of rows from a query result.

---

## 1. SQL Syntax

```sql
SELECT * FROM table_name 
ORDER BY id ASC 
LIMIT ? OFFSET ?;
```

- **`LIMIT`**: Number of rows to return.
- **`OFFSET`**: Number of rows to skip before starting to return rows.

> [!IMPORTANT]
> `mysql2/promise` requires `LIMIT` and `OFFSET` values to be numbers (integers), NOT string representations. Always parse them using `parseInt(value, 10)` before passing to pool query parameters.

---

## 2. Implementation Pattern in `mysql2/promise`

```javascript
import pool from '../config/db.js';

export const getPaginatedUsers = async (page = 1, limit = 10) => {
  // Convert strings to integers explicitly
  const pageNum = Math.max(1, parseInt(page, 10));
  const limitNum = Math.max(1, parseInt(limit, 10));
  const offset = (pageNum - 1) * limitNum;

  // 1. Fetch total count for pagination metadata
  const [[{ total }]] = await pool.query('SELECT COUNT(*) as total FROM users');

  // 2. Fetch paginated records using parameterized query
  const [rows] = await pool.query(
    'SELECT id, name, email, created_at FROM users ORDER BY id DESC LIMIT ? OFFSET ?',
    [limitNum, offset]
  );

  return {
    rows,
    totalRecords: total,
    page: pageNum,
    limit: limitNum
  };
};
```
