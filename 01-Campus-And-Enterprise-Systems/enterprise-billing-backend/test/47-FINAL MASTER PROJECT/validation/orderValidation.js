import { body, validationResult } from 'express-validator';
import { sendError } from '../utils/response.js';

export const validateOrder = [
  body('shipping_address').trim().notEmpty().withMessage('Shipping address is required'),
  body('items').isArray({ min: 1 }).withMessage('Items must be a non-empty array'),
  body('items.*.product_id').isInt().withMessage('Valid product_id is required'),
  body('items.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be at least 1'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, 'Validation error', errors.array().map(e => e.msg), 400);
    }
    next();
  }
];
