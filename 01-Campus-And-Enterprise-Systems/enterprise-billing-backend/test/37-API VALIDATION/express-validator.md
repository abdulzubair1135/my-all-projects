# Complete Guide to `express-validator` package

`express-validator` is a set of Express.js middlewares that wraps validator.js validator and sanitizer functions.

---

## 1. Installation

```bash
npm install express-validator
```

---

## 2. Key Modules to Import

```javascript
import { body, param, query, header, validationResult } from 'express-validator';
```

---

## 3. How `express-validator` Works

1. **Validation Middleware Chain**: Functions like `body()`, `param()`, and `query()` create validation chains.
2. **Sanitization**: Operations like `.trim()`, `.escape()`, `.normalizeEmail()`, and `.toInt()` mutate the value in `req` to clean it up.
3. **Execution**: The chains execute sequentially as request middleware.
4. **Result Collection**: `validationResult(req)` retrieves any errors generated during chain execution.

---

## 4. Custom Validation Rules (`.custom()`)

Custom validators allow you to run complex checks, including checking database values or comparing two fields (e.g. password confirmation).

```javascript
import { body } from 'express-validator';

// Example 1: Password matching check
body('confirmPassword').custom((value, { req }) => {
  if (value !== req.body.password) {
    throw new Error('Password confirmation does not match password');
  }
  return true;
});

// Example 2: Async Database Check (e.g. check duplicate email)
body('email').custom(async (value) => {
  const existingUser = await db.findUserByEmail(value);
  if (existingUser) {
    throw new Error('E-mail already in use');
  }
  return true;
});
```

---

## 5. Structuring Reusable Validation Middlewares

Instead of writing `validationResult(req)` in every single route handler, create a reusable error-handling wrapper function:

```javascript
import { validationResult } from 'express-validator';

// Standardized error handler middleware
export const validate = (validations) => {
  return async (req, res, next) => {
    // Run all validation rules
    for (let validation of validations) {
      await validation.run(req);
    }

    const errors = validationResult(req);
    if (errors.isEmpty()) {
      return next();
    }

    const formattedErrors = errors.array().map(err => ({
      field: err.path,
      message: err.msg
    }));

    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: formattedErrors
    });
  };
};
```

### Clean Usage in Routes
```javascript
import express from 'express';
import { body } from 'express-validator';
import { validate } from './middleware/validate.js';

const router = express.Router();

const userRules = [
  body('username').trim().notEmpty().withMessage('Username is required'),
  body('email').isEmail().withMessage('Valid email is required')
];

router.post('/users', validate(userRules), createUserHandler);
```

---

## 6. Practical Exam Tip Summary

- **`body()`**: Request Body (JSON / form data)
- **`param()`**: URL parameters (`/users/:id`)
- **`query()`**: URL query params (`?page=1&limit=10`)
- **`validationResult(req)`**: Extracts collected errors.
- **HTTP 400**: standard status code returned when validation errors are present.
