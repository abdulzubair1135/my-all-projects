import { body, validationResult } from 'express-validator';

export const validateStudent = [
  body('roll_no').trim().notEmpty().withMessage('Roll number is required'),
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Please provide a valid email'),
  body('department').trim().notEmpty().withMessage('Department is required'),
  body('gpa').isFloat({ min: 0, max: 10 }).withMessage('GPA must be between 0.0 and 10.0'),
  
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
