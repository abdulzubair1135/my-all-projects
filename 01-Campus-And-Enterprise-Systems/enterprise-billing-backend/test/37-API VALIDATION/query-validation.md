# Query String Parameters Validation Guide (`query-validation.md`)

Query parameters (`req.query`) appear after the `?` symbol in a URL (e.g. `/api/products?page=1&limit=10&search=laptop&sort=asc`). They are primarily used for search, filtering, pagination, and sorting operations.

> [!IMPORTANT]
> Query parameters are optional by default in many API endpoints. Use `.optional()` in `express-validator` to validate query parameters only when they are supplied by the client.

---

## 1. Why Validate Query Parameters?

- **Prevent Out-of-Bounds Queries**: Avoid negative page numbers or excessively large limits (`limit=999999`).
- **SQL Sanitization**: Sanitize search queries (`search`) to prevent SQL injection or malicious wildcards.
- **Whitelist Options**: Restrict sort columns and sort orders (`ASC`, `DESC`) to allowed values.

---

## 2. Common `query()` Rules & Sanitizers

| Method / Rule | Description | Example |
| :--- | :--- | :--- |
| `query('page').optional().isInt({ min: 1 })` | Ensures page is an integer >= 1 | `query('page').optional().isInt({ min: 1 })` |
| `query('limit').optional().isInt({ min: 1, max: 100 })` | Caps max page limit | `query('limit').optional().isInt({ min: 1, max: 50 })` |
| `query('search').optional().trim().escape()` | Trims and escapes search string | `query('search').optional().trim().escape()` |
| `query('sortBy').optional().isIn([...])` | Whitelists allowed column names | `query('sortBy').optional().isIn(['name', 'price', 'created_at'])` |
| `query('sortOrder').optional().isIn(['ASC', 'DESC'])` | Whitelists order direction | `query('sortOrder').optional().isIn(['ASC', 'DESC', 'asc', 'desc'])` |

---

## 3. Implementation Example

```javascript
import { query, validationResult } from 'express-validator';

export const validateSearchAndPagination = [
  query('page')
    .optional()
    .isInt({ min: 1 }).withMessage('Page must be an integer greater than 0')
    .toInt(),

  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 }).withMessage('Limit must be an integer between 1 and 100')
    .toInt(),

  query('search')
    .optional()
    .trim()
    .isLength({ max: 50 }).withMessage('Search query cannot exceed 50 characters')
    .escape(), // Escapes HTML entities like <, >, &, ", '

  query('sort')
    .optional()
    .isIn(['id', 'name', 'price', 'createdAt']).withMessage('Invalid sort field'),

  query('order')
    .optional()
    .toLowerCase()
    .isIn(['asc', 'desc']).withMessage('Order must be asc or desc'),

  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Invalid query parameters',
        errors: errors.array().map(err => ({ field: err.path, message: err.msg }))
      });
    }
    next();
  }
];
```

---

## 4. Practical Usage in Express Route

```javascript
import express from 'express';
import { validateSearchAndPagination } from './validators.js';

const router = express.Router();

router.get('/products', validateSearchAndPagination, (req, res) => {
  // Safe defaults if query params are not supplied
  const page = req.query.page || 1;
  const limit = req.query.limit || 10;
  const search = req.query.search || '';
  const sort = req.query.sort || 'id';
  const order = req.query.order || 'asc';

  res.status(200).json({
    success: true,
    message: 'Products query parameters validated',
    data: { page, limit, search, sort, order }
  });
});

export default router;
```
