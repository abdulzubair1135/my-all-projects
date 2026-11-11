import { body, validationResult } from 'express-validator';

export const validateOrder = [
  body('customer_name').trim().notEmpty().withMessage('Customer name is required'),
  body('items').isArray({ min: 1 }).withMessage('Items must be a non-empty array'),
  body('items.*.item_name').trim().notEmpty().withMessage('Item name is required'),
  body('items.*.unit_price').isFloat({ min: 0.01 }).withMessage('Unit price must be > 0'),
  body('items.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be >= 1'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
