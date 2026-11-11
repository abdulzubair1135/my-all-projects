# Text Search Implementation Guide with SQL `LIKE` (`search.md`)

Database text search enables users to search for keywords in specific columns (e.g., searching students by name or email).

---

## 1. Using SQL `LIKE` Operator

The `LIKE` operator matches string patterns using wildcard symbols:
- `%`: Matches zero or more characters.
- `_`: Matches exactly one character.

```sql
SELECT * FROM students WHERE name LIKE '%rahul%';
```

---

## 2. Parameterized Query Pattern in `mysql2/promise`

> [!CAUTION]
> Never concatenate search strings directly into SQL queries (e.g. ``WHERE name LIKE '%${search}%'``). This creates severe SQL Injection vulnerabilities!

### Safe Parameterized Pattern:
```javascript
const searchKeyword = req.query.search || '';
const searchPattern = `%${searchKeyword}%`;

const [rows] = await pool.query(
  'SELECT * FROM students WHERE name LIKE ? OR email LIKE ?',
  [searchPattern, searchPattern]
);
```

---

## 3. Handling Special Wildcard Characters

If a user searches for literal `%` or `_` characters, escape them to prevent wildcard manipulation:

```javascript
export const sanitizeSearchTerm = (term) => {
  return term.replace(/[%_]/g, '\\$&');
};
```
