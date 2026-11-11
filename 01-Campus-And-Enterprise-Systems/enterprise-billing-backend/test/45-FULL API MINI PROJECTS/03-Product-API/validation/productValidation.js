import { body, validationResult } from 'express-validator';

export const validateProduct = [
  body('sku').trim().notEmpty().withMessage('SKU is required'),
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('price').isFloat({ min: 0 }).withMessage('Price must be a positive number'),
  body('stock').isInt({ min: 0 }).withMessage('Stock must be an integer >= 0'),
  body('category').trim().notEmpty().withMessage('Category is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
