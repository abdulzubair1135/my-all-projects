# 08 - req.body Undefined Error

## ERROR
`TypeError: Cannot read properties of undefined (reading 'name')` when accessing `req.body.name`.

---

## WHY IT HAPPENS
Express does not parse JSON body data by default. If `express.json()` middleware is missing or placed after routes, `req.body` will be `undefined`.

---

## HOW TO FIND IT
- `console.log(req.body)` prints `undefined` inside controller.

---

## HOW TO FIX IT
Add `app.use(express.json())` at top of `server.js` **before** route mounting:
```javascript
import express from 'express';

const app = express();

// Parsing middleware (MUST BE BEFORE ROUTES)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/products', productRoutes);
```

---

## COMMON EXAM MISTAKE
Forgetting `app.use(express.json())` or selecting `form-data` in Postman without body parser middleware configured.
