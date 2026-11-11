# SET 02 - Input Validation with Express-Validator

## Question
Design a **Student Admission Portal API** that validates all incoming student payload data using `express-validator` before inserting into MySQL database.

---

## Requirements
1. Validate fields:
   - `roll_no`: Non-empty string.
   - `email`: Valid email format (`isEmail()`).
   - `phone`: Exactly 10 digits (`isMobilePhone('en-IN')` or regex `/^[0-9]{10}$/`).
   - `age`: Integer between 17 and 35.
   - `course`: Must be one of `['BCA', 'BSc', 'BTech']`.
2. Extract validation errors and return `400 Bad Request` with error array.
3. If validation succeeds, pass request to controller via `next()`.

---

## Hints
- Create a dedicated validation middleware file `studentValidation.js`.
- Use `validationResult(req)` inside the middleware function.

---

## Expected Structure
```text
SET-02-VALIDATION/
├── validation/
│   └── studentValidation.js
├── controllers/
│   └── studentController.js
├── routes/
│   └── studentRoutes.js
└── server.js
```

---

## Solution Code

### `validation/studentValidation.js`
```javascript
import { body, validationResult } from 'express-validator';

export const validateAdmission = [
  body('roll_no').trim().notEmpty().withMessage('Roll number is mandatory'),
  body('email').isEmail().withMessage('Please enter a valid email address'),
  body('phone').matches(/^[0-9]{10}$/).withMessage('Phone number must be exactly 10 digits'),
  body('age').isInt({ min: 17, max: 35 }).withMessage('Age must be between 17 and 35'),
  body('course').isIn(['BCA', 'BSc', 'BTech']).withMessage('Course must be BCA, BSc, or BTech'),

  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array().map(err => err.msg)
      });
    }
    next();
  }
];
```

### `routes/studentRoutes.js`
```javascript
import express from 'express';
import { validateAdmission } from '../validation/studentValidation.js';
import { registerStudent } from '../controllers/studentController.js';

const router = express.Router();
router.post('/register', validateAdmission, registerStudent);

export default router;
```

---

## Postman Test Guide
- **Test Bad Data:** Send `POST http://localhost:5000/api/students/register` with `{ "age": 12, "email": "bad-email" }` -> Expect `400` status with error messages array.
- **Test Good Data:** Send `{ "roll_no": "BCA001", "email": "john@test.com", "phone": "9876543210", "age": 20, "course": "BCA" }` -> Expect `201` status.
