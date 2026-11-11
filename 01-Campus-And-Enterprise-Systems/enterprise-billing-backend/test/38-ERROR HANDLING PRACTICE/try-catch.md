# Async Error Handling with `try...catch` in Express (`try-catch.md`)

In modern Node.js applications, database calls and external API operations are asynchronous (using `async/await`). If an error occurs inside an `async` function and is not caught, it will result in an **Unhandled Promise Rejection** or crash the Node process.

---

## 1. The Anatomy of `try...catch` in Async Controllers

```javascript
export const getStudent = async (req, res, next) => {
  try {
    // 1. Asynchronous Database Query
    const [rows] = await pool.query('SELECT * FROM students WHERE id = ?', [req.params.id]);

    if (rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found',
        error: 'RESOURCE_NOT_FOUND'
      });
    }

    // 2. Success Response
    res.status(200).json({
      success: true,
      message: 'Student details fetched successfully',
      data: rows[0]
    });
  } catch (error) {
    // 3. Forward unexpected errors to central error middleware
    next(error);
  }
};
```

---

## 2. Why `next(error)` is Critical

When an error is thrown inside a `try` block (e.g. database connection down, SQL syntax error, syntax crash):
1. Execution immediately jumps to the `catch (error)` block.
2. Passing `error` to `next(error)` delegates error handling to Express's central 4-parameter error middleware `(err, req, res, next)`.
3. This guarantees that your server sends a clean JSON error response instead of hanging or crashing.

---

## 3. Async Wrapper Utility (`asyncHandler`)

To eliminate repeating `try...catch` blocks across dozens of controllers, use an `asyncHandler` higher-order function:

```javascript
// utils/asyncHandler.js
export const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};
```

### Usage:
```javascript
import { asyncHandler } from '../utils/asyncHandler.js';

export const getStudent = asyncHandler(async (req, res) => {
  const [rows] = await pool.query('SELECT * FROM students WHERE id = ?', [req.params.id]);
  if (rows.length === 0) {
    return res.status(404).json({ success: false, message: 'Student not found' });
  }
  res.status(200).json({ success: true, data: rows[0] });
});
```

---

## 4. Summary Checklist for BCA Practical Exams

- Wrap every database operation (`await pool.query(...)`) inside a `try...catch` block.
- Always call `next(error)` in the `catch` block for unhandled server errors.
- Never ignore caught errors (e.g., empty catch block `catch (e) {}`).
