# Route Parameters (`req.params`) Guide

## 1. What are Route Parameters?
Route parameters are named URL segments used to capture values specified at their position in the URL. Captured values are populated in the `req.params` object as key-value string pairs.

---

## 2. Syntax & Matching Examples

| Route Pattern | Target URL | `req.params` Object |
|---------------|------------|---------------------|
| `/users/:id` | `/users/42` | `{ id: "42" }` |
| `/books/:category/:id` | `/books/fiction/101` | `{ category: "fiction", id: "101" }` |
| `/flights/:from-:to` | `/flights/DEL-BOM` | `{ from: "DEL", to: "BOM" }` |

---

## 3. Express Code Example (ES Modules)

```js
import express from 'express';
const app = express();

// Single parameter
app.get('/api/users/:id', (req, res) => {
  const userId = parseInt(req.params.id, 10);
  if (isNaN(userId)) {
    return res.status(400).json({ success: false, message: "Invalid user ID format", error: "BAD_PARAM" });
  }

  res.status(200).json({ success: true, data: { userId } });
});

// Multiple parameters
app.get('/api/departments/:deptId/employees/:empId', (req, res) => {
  const { deptId, empId } = req.params;
  res.status(200).json({
    success: true,
    data: { department: deptId, employee: empId }
  });
});
```

---

## 4. Key Rules for Practical Exams
- Parameters are mandatory in the URL path. Requesting `/api/users/` will not match `/api/users/:id`.
- Parameter values are always `string` types. Explicit type conversion (`parseInt` or `Number()`) is mandatory when querying numeric database primary keys.
