# Express.js Middleware Deep Dive

## 1. What is Middleware?
Middleware functions are functions that have access to the request object (`req`), the response object (`res`), and the `next` function in the application’s request-response cycle.

### Execution Cycle:
```
Request ---> [ Middleware 1 ] ---> [ Middleware 2 ] ---> [ Controller Handler ] ---> Response
```

---

## 2. Five Types of Express Middleware

1. **Application-level Middleware**: Bound to `app` using `app.use()`.
2. **Router-level Middleware**: Bound to an instance of `express.Router()`.
3. **Built-in Middleware**: Express provided (`express.json()`, `express.urlencoded()`, `express.static()`).
4. **Third-party Middleware**: Installed via npm (`cors`, `morgan`, `helmet`).
5. **Error-handling Middleware**: Accepts 4 arguments `(err, req, res, next)`.

---

## 3. Code Examples (ES Modules)

### Custom Logger Middleware:
```js
import express from 'express';

const app = express();

// Application-level Middleware
const loggerMiddleware = (req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next(); // Pass control to the next middleware/route handler
};

app.use(loggerMiddleware);
app.use(express.json());

// Auth Middleware example
const checkAuth = (req, res, next) => {
  const token = req.headers['authorization'];
  if (!token) {
    return res.status(401).json({ success: false, message: "Unauthorized", error: "TOKEN_MISSING" });
  }
  next();
};

app.get('/api/dashboard', checkAuth, (req, res) => {
  res.status(200).json({ success: true, message: "Welcome to protected dashboard" });
});

// Centralized Error-handling Middleware
app.use((err, req, res, next) => {
  console.error("Global Error Caught:", err.stack);
  res.status(500).json({
    success: false,
    message: "Internal Server Error",
    error: err.message
  });
});

app.listen(5000, () => console.log("Server listening on port 5000"));
```

---

## 4. Exam Viva Questions
- **Q**: What happens if you forget to call `next()` inside a custom middleware?
  - **A**: The request hangs indefinitely, and the client receives a timeout because the control stream never progresses.
- **Q**: How does Express recognize an Error Handling middleware?
  - **A**: By declaring exactly 4 parameters in the function signature: `(err, req, res, next)`.
