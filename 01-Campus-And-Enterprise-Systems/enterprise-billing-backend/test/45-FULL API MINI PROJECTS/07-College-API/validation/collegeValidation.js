import { body, validationResult } from 'express-validator';

export const validateCourse = [
  body('course_code').trim().notEmpty().withMessage('Course code required'),
  body('course_name').trim().notEmpty().withMessage('Course name required'),
  body('credits').isInt({ min: 1, max: 10 }).withMessage('Credits must be between 1 and 10'),
  body('department_id').isInt().withMessage('Valid department_id required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
