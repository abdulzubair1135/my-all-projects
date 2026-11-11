# Express Request Object (`req`) Guide

## 1. What is `req`?
The `req` object represents the HTTP request and has properties for the request query string, parameters, body, HTTP headers, etc.

---

## 2. Key Properties of `req`

| Property | Description | Example |
|----------|-------------|---------|
| `req.params` | Object containing URL path parameters | `/users/:id` -> `{ id: "5" }` |
| `req.query` | Object containing URL query parameters | `?page=1&limit=10` -> `{ page: "1", limit: "10" }` |
| `req.body` | Parsed request body payload (requires `express.json()`) | `{ "name": "Rahul" }` |
| `req.headers` | Object containing request HTTP headers | `req.headers['authorization']` |
| `req.method` | String corresponding to the HTTP method | `"GET"`, `"POST"` |
| `req.url` / `req.path` | Requested path URL string | `"/api/students"` |
| `req.ip` | Remote IP address of the client | `"127.0.0.1"` |

---

## 3. Code Example

```js
import express from 'express';
const app = express();

app.use(express.json());

app.post('/api/courses/:courseId', (req, res) => {
  const courseId = req.params.courseId;          // URL Param
  const viewMode = req.query.mode || 'full';     // Query Param
  const authHeader = req.get('authorization');   // Header helper
  const payload = req.body;                      // JSON Body

  res.status(200).json({
    success: true,
    data: {
      courseId,
      viewMode,
      authHeader,
      payload,
      method: req.method,
      ip: req.ip
    }
  });
});
```

---

## 4. Exam Notes
- `req.params` values are always **strings**. Convert to numbers using `parseInt(req.params.id, 10)` before DB queries.
- `req.body` is `undefined` unless `app.use(express.json())` middleware is registered.
