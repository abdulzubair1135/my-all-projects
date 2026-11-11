# 500 Internal Server Error Guide (`500-errors.md`)

The `500 Internal Server Error` HTTP status code indicates that the server encountered an unexpected condition that prevented it from fulfilling the request.

---

## 1. Causes of HTTP 500 Errors

- Unhandled database connection failures (e.g. MySQL server offline).
- Unhandled code bugs (e.g. `TypeError: Cannot read properties of undefined`).
- Network timeouts, third-party service crashes, or memory leaks.

---

## 2. Standard 500 Response Format

> [!CAUTION]
> In production environments, never expose full database errors or stack traces to the client in 500 responses! Exposing stack traces exposes system architecture details to potential attackers.

### Production Response (Safe)
```json
{
  "success": false,
  "message": "Internal Server Error. Please try again later.",
  "error": "SERVER_ERROR"
}
```

### Development Response (Debugging)
```json
{
  "success": false,
  "message": "Cannot read property 'query' of undefined",
  "error": "TypeError",
  "stack": "TypeError: Cannot read property 'query' of undefined at getStudent..."
}
```

---

## 3. Best Practices for 500 Handling

1. Always log full error stack traces server-side (`console.error(err)`).
2. Catch errors in `async` handlers using `try...catch` and delegate to `next(err)`.
3. Keep database credentials safely in `.env`.
4. Ensure MySQL pool connections handle reconnection gracefully.
