# 14 - Unhandled Promise Rejection Error

## ERROR
`UnhandledPromiseRejectionWarning: Unhandled promise rejection.` or node application crashing silently without standard JSON response.

---

## WHY IT HAPPENS
An exception occurred inside an `async` function, but there was no `try...catch` block to handle it and no error handling middleware configured in Express.

---

## HOW TO FIND IT
- Terminal output shows `UnhandledPromiseRejectionWarning` or `node:internal/process/promises`.

---

## HOW TO FIX IT
1. Always catch errors in async functions:
```javascript
export const getById = async (req, res, next) => {
    try {
        const [rows] = await pool.query('SELECT * FROM items WHERE id = ?', [req.params.id]);
        if (rows.length === 0) {
            return res.status(404).json({ success: false, message: 'Item not found' });
        }
        res.json({ success: true, data: rows[0] });
    } catch (error) {
        next(error); // Pass to global error middleware
    }
};
```
2. Add global error middleware at bottom of `server.js`:
```javascript
app.use((err, req, res, next) => {
    console.error('Unhandled Error:', err);
    res.status(err.status || 500).json({
        success: false,
        message: 'Internal Server Error',
        error: err.message
    });
});
```

---

## COMMON EXAM MISTAKE
Forgetting to wrap database operations in `try...catch` blocks, causing DB errors (like missing tables) to crash the Node process.
