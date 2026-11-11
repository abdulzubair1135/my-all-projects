# 03 - Cannot Find Module

## ERROR
`Error: Cannot find module 'express'` or `Error: Cannot find module './routes/productRoutes.js'`

---

## WHY IT HAPPENS
1. Required npm package is not installed in `node_modules`.
2. Relative file path in `import` statement is incorrect (missing `./` or `../`).
3. File extension `.js` omitted in ES Module project.

---

## HOW TO FIND IT
- Check stack trace error message: `Cannot find module 'XYZ'`.
- If `XYZ` is a package name (e.g., `jsonwebtoken`), npm package is missing.
- If `XYZ` starts with `./` or `../`, local file path is wrong.

---

## HOW TO FIX IT
1. If missing npm package:
```bash
npm install express mysql2 dotenv bcrypt jsonwebtoken express-validator cors
```
2. If missing local file path, check your relative path from current file:
```javascript
// Correct relative import:
import productRoutes from './routes/productRoutes.js';
```

---

## COMMON EXAM MISTAKE
Typing `import db from 'db.js'` instead of `import db from './db.js'`. Without `./`, Node looks inside `node_modules` directory!
