# Express Response Object (`res`) Guide

## 1. What is `res`?
The `res` object represents the HTTP response that an Express app sends when it gets an HTTP request.

---

## 2. Commonly Used `res` Methods

| Method | Purpose | Usage Example |
|--------|---------|---------------|
| `res.status(code)` | Set the HTTP status code for the response | `res.status(201)` |
| `res.json(body)` | Send a JSON response with header `Content-Type: application/json` | `res.json({ success: true })` |
| `res.send(body)` | Send plain text, HTML, or buffer | `res.send('<h1>Hello World</h1>')` |
| `res.setHeader(name, val)` | Set a custom HTTP response header | `res.setHeader('X-Total-Count', 100)` |
| `res.redirect(url)` | Redirect a request to another URL | `res.redirect('/login')` |
| `res.download(path)` | Prompt user to download a file | `res.download('./report.pdf')` |
| `res.end()` | End the response process without sending data | `res.status(204).end()` |

---

## 3. Standard Response Format Rule (Exam & Production Standard)

Always maintain consistent API response structures across all routes!

### Success Standard Structure:
```js
res.status(200).json({
  success: true,
  message: "Operation completed successfully",
  data: [ { id: 1, name: "Student A" } ]
});
```

### Error Standard Structure:
```js
res.status(400).json({
  success: false,
  message: "Invalid input parameters",
  error: "VALIDATION_FAILED"
});
```

---

## 4. Method Chaining Pattern
Express allows chaining status with json/send:
```js
return res.status(201).json({ success: true, message: "Resource created" });
```
> **Important**: Always use `return` when sending a response inside conditional blocks to prevent sending multiple responses ("Cannot set headers after they are sent to the client" error).
