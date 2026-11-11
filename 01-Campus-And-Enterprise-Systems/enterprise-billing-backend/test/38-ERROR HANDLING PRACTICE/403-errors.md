# 403 Forbidden Error Guide (`403-errors.md`)

The `403 Forbidden` HTTP status code indicates that the server understands the client's identity (the client IS authenticated), but the client does NOT possess sufficient authority or permissions to access the requested resource.

---

## 1. 401 vs 403 Difference

- **401 Unauthorized**: "Who are you? I don't recognize your token or identity."
- **403 Forbidden**: "I know who you are (e.g. Student role), but you are not allowed to access this resource (e.g. Admin route)."

---

## 2. Standard 403 Response Format

```json
{
  "success": false,
  "message": "Permission denied. Admin role required to perform this action.",
  "error": "FORBIDDEN"
}
```

---

## 3. Role-Based Authorization Middleware Example

```javascript
export const authorizeRoles = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'Access forbidden: Insufficient permissions',
        error: `Required role: ${allowedRoles.join(' or ')}`
      });
    }
    next();
  };
};
```
