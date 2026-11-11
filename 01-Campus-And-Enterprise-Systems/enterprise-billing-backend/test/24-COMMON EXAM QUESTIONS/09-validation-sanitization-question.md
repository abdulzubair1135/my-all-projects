# 09 - Input Validation & Sanitization Exam Question

## QUESTION
Create request validation rules using `express-validator` for user registration: sanitize input (trim, normalizeEmail) and enforce rules (email format, strong password length, non-empty name).

---

## REQUIREMENTS
- Reject empty fields with descriptive error messages.
- Return structured array of error objects.

---

## FILES REQUIRED
1. `middleware/userValidation.js`
2. `routes/authRoutes.js`

---

## CODING ORDER
1. Import `body` & `validationResult` from `express-validator`.
2. Write validation array rules:
```javascript
import { body, validationResult } from 'express-validator';

export const registerValidation = [
    body('name').trim().notEmpty().withMessage('Name is required'),
    body('email').trim().isEmail().normalizeEmail().withMessage('Valid email is required'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
    (req, res, next) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ success: false, errors: errors.array() });
        }
        next();
    }
];
```
3. Attach to route definition.

---

## API FLOW
`POST /api/auth/register` -> `registerValidation` sanitizes & validates fields -> Passes to Controller if valid.

---

## POSTMAN TEST
Send POST with `{"name": "", "email": "bademail", "password": "12"}` -> Expect 400 Bad Request with array of 3 errors.

---

## COMMON MISTAKES
- Forgetting `normalizeEmail()` or `.trim()` to remove unwanted space characters.
