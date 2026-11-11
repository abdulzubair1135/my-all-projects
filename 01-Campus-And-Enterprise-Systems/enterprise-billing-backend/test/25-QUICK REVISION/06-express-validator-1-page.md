# Express Validator One-Page Quick Revision Sheet

## Standard Validation Pattern
```javascript
import { body, validationResult } from 'express-validator';

export const validateUser = [
    body('name').trim().notEmpty().withMessage('Name is required'),
    body('email').trim().isEmail().normalizeEmail().withMessage('Valid email required'),
    body('password').isLength({ min: 6 }).withMessage('Password must be 6+ chars'),
    (req, res, next) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({
                success: false,
                message: 'Validation Error',
                errors: errors.array()
            });
        }
        next();
    }
];
```

---

## Commonly Used Rules Cheat Sheet
- `.notEmpty()`: String cannot be empty
- `.isEmail()`: Must be valid email address
- `.isLength({ min: 5, max: 20 })`: Enforce string length limits
- `.isFloat({ gt: 0 })`: Must be floating point number greater than 0
- `.isInt({ min: 0 })`: Must be integer 0 or greater
- `.trim()`: Remove leading/trailing spaces
- `.normalizeEmail()`: Canonicalize email address
