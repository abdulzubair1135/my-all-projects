# 11 - Express Validator Errors

## ERROR
Validation rules defined in route do not reject bad requests, OR valid requests fail with 400 Bad Request.

---

## WHY IT HAPPENS
1. `validationResult(req)` check function is omitted in middleware/controller.
2. Incorrect validation chains (e.g. `isEmail()` placed on `name` field).
3. Field names in validator rules do not match JSON body payload keys.

---

## HOW TO FIND IT
- Check controller logic to see if `validationResult(req)` is invoked.
- Inspect JSON response `errors` array in Postman.

---

## HOW TO FIX IT
1. Define validation rules array in middleware file or route file:
```javascript
import { body, validationResult } from 'express-validator';

export const validateProduct = [
    body('name').trim().notEmpty().withMessage('Product name is required'),
    body('price').isFloat({ gt: 0 }).withMessage('Price must be greater than 0'),
    body('stock').isInt({ min: 0 }).withMessage('Stock must be a positive integer'),
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
2. Attach `validateProduct` before controller in route definition:
```javascript
router.post('/', validateProduct, createProduct);
```

---

## COMMON EXAM MISTAKE
Adding validation chain `[body('email').isEmail()]` to route file, but forgetting to include `validationResult(req)` check step, so invalid requests pass through to controller.
