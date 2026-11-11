# Dynamic Database Sorting Guide (`sorting.md`)

Sorting allows API clients to dictate the order of returned records using query parameters such as `?sortBy=price&sortOrder=DESC`.

---

## 1. Security Risk & Column Whitelisting

SQL column names and `ASC`/`DESC` keywords cannot be passed as prepared statement bindings `?` in MySQL parameters. They must be inserted directly into SQL query strings.

> [!WARNING]
> Because sort columns are inserted directly, you MUST whitelist allowed column names to prevent SQL Injection.

---

## 2. Whitelisting Implementation Pattern

```javascript
// Whitelist allowed column names
const ALLOWED_SORT_COLUMNS = ['id', 'name', 'created_at', 'marks'];
const ALLOWED_ORDERS = ['ASC', 'DESC'];

export const getSortedStudents = async (req, res) => {
  let { sortBy = 'id', sortOrder = 'ASC' } = req.query;

  // Validate column against whitelist
  if (!ALLOWED_SORT_COLUMNS.includes(sortBy)) {
    sortBy = 'id';
  }

  // Validate order against whitelist
  sortOrder = sortOrder.toUpperCase();
  if (!ALLOWED_ORDERS.includes(sortOrder)) {
    sortOrder = 'ASC';
  }

  // Safe SQL String Interpolation after strict whitelisting
  const sql = `SELECT * FROM students ORDER BY ${sortBy} ${sortOrder}`;
  const [rows] = await pool.query(sql);

  res.json({ success: true, data: rows });
};
```
