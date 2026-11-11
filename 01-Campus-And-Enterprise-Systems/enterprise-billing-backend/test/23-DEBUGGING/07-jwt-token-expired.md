# 07 - JWT Token Expired Error

## ERROR
`TokenExpiredError: jwt expired`

---

## WHY IT HAPPENS
The token passed in request header has exceeded its lifespan specified in `expiresIn` (e.g. `'1m'`, `'1h'`).

---

## HOW TO FIND IT
- `jwt.verify()` throws an error with `err.name === 'TokenExpiredError'`.

---

## HOW TO FIX IT
1. Increase token expiration time during `jwt.sign()` for exam testing:
```javascript
const token = jwt.sign(
    { id: user.id, email: user.email, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '24h' } // Set to 24h for exam testing convenience
);
```
2. Re-login via `/api/auth/login` endpoint in Postman to generate a fresh token.

---

## COMMON EXAM MISTAKE
Setting token expiry to `'5s'` or `'1m'` while developing, causing authorization to fail while demonstrating to the examiner.
