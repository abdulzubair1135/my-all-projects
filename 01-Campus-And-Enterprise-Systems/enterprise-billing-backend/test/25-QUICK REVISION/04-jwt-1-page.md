# JWT (JSON Web Token) One-Page Quick Revision Sheet

## What is JWT?
JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It consists of three parts separated by dots (`.`): `Header.Payload.Signature`.

---

## 1. Generating a Token (Login Controller)
```javascript
import jwt from 'jsonwebtoken';

const token = jwt.sign(
    { id: user.id, email: user.email, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
);
```

---

## 2. Verifying Token (Auth Middleware)
```javascript
import jwt from 'jsonwebtoken';

export const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Extract token from 'Bearer <token>'

    if (!token) return res.status(401).json({ success: false, message: 'Access token required' });

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        return res.status(401).json({ success: false, message: 'Invalid or expired token' });
    }
};
```
