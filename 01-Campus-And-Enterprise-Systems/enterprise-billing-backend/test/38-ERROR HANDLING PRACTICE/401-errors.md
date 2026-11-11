# 401 Unauthorized Error Guide (`401-errors.md`)

The `401 Unauthorized` HTTP status code indicates that the request lacks valid authentication credentials. It is returned when an unauthenticated user attempts to access a protected API route.

---

## 1. When to Return HTTP 401

- Missing `Authorization` header in the HTTP request.
- Invalid or malformed JWT token string.
- Expired JWT token.
- Incorrect login credentials (invalid password during user authentication).

---

## 2. Standard 401 Response Format

```json
{
  "success": false,
  "message": "Access denied. Authentication token missing or invalid.",
  "error": "UNAUTHORIZED_ACCESS"
}
```

---

## 3. JWT Middleware Example

```javascript
import jwt from 'jsonwebtoken';

export const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      success: false,
      message: 'Access token missing or malformed',
      error: 'UNAUTHORIZED'
    });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secretkey');
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({
      success: false,
      message: 'Invalid or expired token',
      error: err.message
    });
  }
};
```
