# Route Parameters Validation Guide (`params-validation.md`)

Route parameters (`req.params`) are variable segments extracted directly from the URL path, such as `/api/users/:id` or `/api/products/:category/:id`. Validating route parameters prevents database errors caused by bad data types (e.g. passing a string `"abc"` where a numeric primary key integer is expected).

> [!IMPORTANT]
> Express captures route params as strings by default! Use `param('id').isInt().toInt()` to convert string parameters into JavaScript numbers.

---

## 1. Why Validate Route Parameters?

1. **Prevent SQL Errors**: Passing string IDs to SQL queries expecting numeric IDs can cause database syntax or execution errors.
2. **Prevent Database Injections**: Unsanitized parameters can be exploited if directly concatenated.
3. **Early 400 Responses**: Stops request processing immediately if the ID is invalid, saving server computation time.

---

## 2. Common `param()` Rules & Methods

| Rule / Method | Description | Example |
| :--- | :--- | :--- |
| `param('id').isInt()` | Checks if param is a valid integer | `param('id').isInt({ min: 1 })` |
| `param('id').toInt()` | Sanitizer: Converts param string to integer in `req.params` | `param('id').toInt()` |
| `param('uuid').isUUID()` | Validates UUID format (v4) | `param('uuid').isUUID()` |
| `param('slug').isSlug()` | Checks if valid URL slug (lowercase alphanumeric with hyphens) | `param('slug').isSlug()` |
| `param('code').isAlpha()` | Checks if param contains only letters | `param('code').isAlpha()` |

---

## 3. Implementation Example

```javascript
import { param, validationResult } from 'express-validator';

// Middleware for validating route parameter :id
export const validateUserIdParam = [
  param('id')
    .exists().withMessage('User ID is required in URL')
    .isInt({ min: 1 }).withMessage('User ID must be a positive integer')
    .toInt(), // Converts req.params.id to a number

  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Invalid URL parameters',
        errors: errors.array().map(err => ({ field: err.path, message: err.msg }))
      });
    }
    next();
  }
];
```

---

## 4. Route Attachment Example

```javascript
import express from 'express';
import { validateUserIdParam } from './validators.js';
import { getUserById, deleteUser } from './user.controller.js';

const router = express.Router();

// Validate :id parameter for GET and DELETE routes
router.get('/users/:id', validateUserIdParam, getUserById);
router.delete('/users/:id', validateUserIdParam, deleteUser);

export default router;
```

---

## 5. Exam Checklist

> [!NOTE]
> - Always place `param('id')` validation before the controller execution.
> - Combine `.isInt({ min: 1 })` and `.toInt()` for database primary key IDs.
> - Ensure consistent HTTP 400 responses on failure.
