# 12 - Async / Await Error Handling

## ERROR
Server crashes or hangs indefinitely when an error occurs during database query inside async route handler.

---

## WHY IT HAPPENS
1. `await` keyword missing before `pool.query()`, returning an un-awaited Promise object instead of query result array.
2. Missing `try...catch` block around `await` operation.
3. Controller function missing `async` keyword in signature.

---

## HOW TO FIND IT
- Check controller function header for `async`.
- Check database calls for `await`.
- Observe if Postman request times out (spins infinitely without response).

---

## HOW TO FIX IT
Always wrap async controllers with `try...catch` blocks and standard JSON error response:

```javascript
export const getAllProducts = async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT * FROM products');
        return res.status(200).json({
            success: true,
            message: 'Products retrieved successfully',
            data: rows
        });
    } catch (error) {
        console.error('Error fetching products:', error);
        return res.status(500).json({
            success: false,
            message: 'Failed to retrieve products',
            error: error.message
        });
    }
};
```

---

## COMMON EXAM MISTAKE
Writing `const rows = pool.query('SELECT * FROM products')` without `await` and destructuring `[rows]`. `mysql2/promise` returns `[rows, fields]`.
