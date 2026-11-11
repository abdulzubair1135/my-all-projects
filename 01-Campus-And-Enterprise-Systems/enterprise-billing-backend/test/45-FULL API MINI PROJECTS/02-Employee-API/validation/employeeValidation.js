import { body, validationResult } from 'express-validator';

export const validateEmployee = [
  body('emp_code').trim().notEmpty().withMessage('Employee code is required'),
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Valid email required'),
  body('designation').trim().notEmpty().withMessage('Designation is required'),
  body('salary').isFloat({ min: 0 }).withMessage('Salary must be a positive number'),
  body('department').trim().notEmpty().withMessage('Department is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
