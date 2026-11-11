# 06 - JWT Invalid Token Error

## ERROR
`JsonWebTokenError: invalid signature` or `JsonWebTokenError: jwt malformed`

---

## WHY IT HAPPENS
1. JWT Secret in `jwt.verify(token, process.env.JWT_SECRET)` does not match secret used during `jwt.sign()`.
2. Token string sent in `Authorization` header is corrupted or missing `"Bearer "` prefix parsing.
3. Postman sent incorrect token.

---

## HOW TO FIND IT
- Catch block in auth middleware prints `err.name === 'JsonWebTokenError'`.

---

## HOW TO FIX IT
1. Ensure `JWT_SECRET` is set in `.env`:
```env
JWT_SECRET=super_secret_exam_key_123
```
2. In Auth Middleware (`authMiddleware.js`), extract Bearer token correctly:
```javascript
import jwt from 'jsonwebtoken';

export const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ success: false, message: 'Token missing' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        return res.status(401).json({ success: false, message: 'Invalid or expired token', error: err.message });
    }
};
```

---

## COMMON EXAM MISTAKE
Forgetting `authHeader.split(' ')[1]` and passing `"Bearer eyJ..."` directly into `jwt.verify()`.
