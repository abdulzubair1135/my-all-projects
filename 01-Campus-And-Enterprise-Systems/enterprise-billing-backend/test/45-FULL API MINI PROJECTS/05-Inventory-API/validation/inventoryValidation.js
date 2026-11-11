import { body, validationResult } from 'express-validator';

export const validateInventory = [
  body('item_code').trim().notEmpty().withMessage('Item code is required'),
  body('item_name').trim().notEmpty().withMessage('Item name is required'),
  body('quantity').isInt({ min: 0 }).withMessage('Quantity must be a positive integer'),
  body('min_level').isInt({ min: 0 }).withMessage('Min level must be a positive integer'),
  body('supplier').trim().notEmpty().withMessage('Supplier is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
