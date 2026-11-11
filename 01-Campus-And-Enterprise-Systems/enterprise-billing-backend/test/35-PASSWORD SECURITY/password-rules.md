# Password Security Rules & Validation Best Practices

## 1. Golden Rules for Password Security

1. **Minimum Length Standard**: Enforce at least 6 to 8 characters (NIST recommends 8+).
2. **Complexity Rules**: Require a mix of uppercase letters, lowercase letters, numbers, and special characters (`@`, `#`, `$`, `%`).
3. **Never Log Passwords**: Ensure `console.log(req.body)` does not log raw passwords in production logs!
4. **Never Store Plaintext**: Hash immediately before persisting to MySQL database.
5. **Never Return Passwords in Responses**: Always omit the password field when returning user objects in API JSON responses.

---

## 2. Express-Validator Rule Pattern

```js
import { body } from 'express-validator';

export const passwordCheckRule = body('password')
  .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
  .matches(/[A-Z]/).withMessage('Password must contain at least one uppercase letter')
  .matches(/[a-z]/).withMessage('Password must contain at least one lowercase letter')
  .matches(/[0-9]/).withMessage('Password must contain at least one number')
  .matches(/[@$!%*?&]/).withMessage('Password must contain at least one special character');
```
