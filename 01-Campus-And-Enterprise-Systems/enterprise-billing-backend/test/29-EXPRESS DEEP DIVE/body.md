# Express Request Body (`req.body`) Guide

## 1. What is `req.body`?
`req.body` contains key-value pairs of data submitted in the HTTP request body. It is typically used with `POST`, `PUT`, and `PATCH` requests to send JSON objects or form data.

---

## 2. Requirement for Body Parsing Middleware
By default, Express does NOT parse incoming HTTP request bodies. You must use built-in parsing middleware:

```js
import express from 'express';

const app = express();

// Middleware to parse application/json payload
app.use(express.json());

// Middleware to parse URL-encoded form submissions (HTML forms)
app.use(express.urlencoded({ extended: true }));
```

---

## 3. Code Example

```js
import express from 'express';

const app = express();
app.use(express.json());

app.post('/api/students', (req, res) => {
  const { name, email, age, course } = req.body;

  // Manual basic validation check
  if (!name || !email) {
    return res.status(400).json({
      success: false,
      message: "Name and email are mandatory fields",
      error: "MISSING_FIELDS"
    });
  }

  res.status(201).json({
    success: true,
    message: "Student created successfully",
    data: { id: Date.now(), name, email, age, course }
  });
});
```

---

## 4. Common Pitfalls in Practical Exams
1. **`req.body` is `undefined`**: Missing `app.use(express.json())` at top of `server.js` before routes.
2. **Postman Header Mismatch**: Forgetting to set `Content-Type: application/json` in Postman header while sending raw body JSON.
