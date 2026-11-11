# 01 - Server Not Starting

## ERROR
Terminal displays syntax errors, `MODULE_NOT_FOUND`, or exits immediately without logging `"Server running on port..."`.

---

## WHY IT HAPPENS
1. Missing `import` statements or incorrect relative file paths in `server.js`.
2. Syntax errors like missing brackets `}` or missing semicolons/commas.
3. Forgotten `app.listen()` statement.
4. Top-level code throwing an unhandled exception during initialization.

---

## HOW TO FIND IT
- Check your terminal output line by line.
- Look at the line number in the stack trace (e.g. `at file:///C:/backend/test/server.js:15:2`).
- Check if `node server.js` produces any output at all.

---

## HOW TO FIX IT
1. Open `server.js` and verify `app.listen()` exists at the end:
```javascript
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```
2. Verify all imported files exist at the specified relative paths (`import productRoutes from './routes/productRoutes.js'`).
3. Note the `.js` extension required when using ES Modules (`"type": "module"`).

---

## COMMON EXAM MISTAKE
Omitting the `.js` file extension in ES module relative imports (e.g., writing `import db from './config/db'` instead of `import db from './config/db.js'`).
