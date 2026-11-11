# Request Body Validation Guide (`express-validator`)

In Express.js REST APIs, validating the incoming request body (`req.body`) is critical to ensure data integrity, prevent invalid database operations, and block malicious payloads.

> [!IMPORTANT]
> Never trust client input! Always sanitize and validate `req.body` parameters on the server side before passing them to database queries or business logic.

---

## 1. What is Body Validation?

When a client sends a `POST`, `PUT`, or `PATCH` request with a JSON payload, the data resides inside `req.body`. Body validation verifies that:
- Required fields are present.
- Data types match expectations (e.g., string, integer, email, boolean).
- Values fit within specified boundaries (e.g., min length, age range, valid email format).
- Whitespace is sanitized (`trim()`), and harmful scripts are escaped (`escape()`).

---

## 2. Common `express-validator` Body Rules

| Method / Rule | Description | Example |
| :--- | :--- | :--- |
| `body('field').notEmpty()` | Ensures the field is present and not empty | `body('name').notEmpty()` |
| `body('field').isEmail()` | Checks if the string is a valid email | `body('email').isEmail()` |
| `body('field').isLength({ min, max })` | Enforces string length constraints | `body('password').isLength({ min: 6 })` |
| `body('field').isNumeric()` / `isInt()` | Checks for numeric or integer values | `body('age').isInt({ min: 18 })` |
| `body('field').trim()` | Sanitizes string by stripping surrounding whitespace | `body('username').trim()` |
| `body('field').normalizeEmail()` | Canonicalizes email address (e.g. lowercase) | `body('email').normalizeEmail()` |
| `body('field').isIn([...])` | Checks if value is within allowed array | `body('role').isIn(['student', 'admin'])` |

---

## 3. Step-by-Step Code Pattern

### Step A: Define Validation Middleware Array
```javascript
import { body, validationResult } from 'express-validator';

export const validateUserRegistration = [
  body('name')
    .trim()
    .notEmpty().withMessage('Name is required')
    .isLength({ min: 3 }).withMessage('Name must be at least 3 characters long'),
  
  body('email')
    .trim()
    .notEmpty().withMessage('Email is required')
    .isEmail().withMessage('Please provide a valid email address')
    .normalizeEmail(),

  body('password')
    .notEmpty().withMessage('Password is required')
    .isLength({ min: 6 }).withMessage('Password must be at least 6 characters long'),

  body('age')
    .optional()
    .isInt({ min: 18, max: 100 }).withMessage('Age must be an integer between 18 and 100'),

  // Validation Result Checker
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array().map(err => ({ field: err.path, message: err.msg }))
      });
    }
    next();
  }
];
```

### Step B: Attach to Route Handler
```javascript
import express from 'express';
import { validateUserRegistration } from './validators.js';
import { registerUser } from './user.controller.js';

const router = express.Router();

router.post('/register', validateUserRegistration, registerUser);

export default router;
```

---

## 4. BCA Exam Practical Tips

> [!TIP]
> - Always import `body` and `validationResult` from `'express-validator'`.
> - Always return HTTP status `400 Bad Request` when validation fails.
> - Structure response using the standard JSON format: `{ success: false, message: "...", errors: [...] }`.
