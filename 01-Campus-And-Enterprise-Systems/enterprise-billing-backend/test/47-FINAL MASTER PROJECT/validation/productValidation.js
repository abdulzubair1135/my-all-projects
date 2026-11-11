import { body, validationResult } from 'express-validator';
import { sendError } from '../utils/response.js';

export const validateProduct = [
  body('sku').trim().notEmpty().withMessage('Product SKU is required'),
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('price').isFloat({ min: 0.01 }).withMessage('Price must be greater than 0'),
  body('stock').isInt({ min: 0 }).withMessage('Stock must be an integer >= 0'),
  body('category_id').isInt().withMessage('Valid category_id is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation error', errors.array().map(e => e.msg), 400);
    }
    next();
  }
];
