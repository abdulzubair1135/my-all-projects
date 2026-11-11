# SET 03 - JWT Authentication & Bcrypt Hashing

## Question
Implement User Registration, Bcrypt Password Hashing, JWT Login, and a Protected Profile API route in Express.js.

---

## Requirements
1. Hash user passwords using `bcrypt.hash()` with salt rounds = 10 before saving to DB.
2. Verify passwords on login using `bcrypt.compare()`.
3. Generate JWT signed token with `jsonwebtoken` package on successful login (`expiresIn: '1h'`).
4. Build `verifyToken` middleware to protect `/api/auth/profile` route by checking the `Authorization: Bearer <token>` header.

---

## Hints
- `const token = jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' })`
- `const decoded = jwt.verify(token, SECRET)`

---

## Expected Structure
```text
SET-03-AUTH-JWT/
├── middleware/
│   └── authMiddleware.js
├── controllers/
│   └── authController.js
├── routes/
│   └── authRoutes.js
└── server.js
```

---

## Solution Code

### `middleware/authMiddleware.js`
```javascript
import jwt from 'jsonwebtoken';

export const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, message: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secretkey');
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ success: false, message: 'Invalid or expired token' });
  }
};
```

---

## Postman Test Guide
1. `POST /api/auth/login` -> Copy `token` string from response.
2. `GET /api/auth/profile` -> Go to `Headers` tab -> Add `Authorization` = `Bearer <token>`.
