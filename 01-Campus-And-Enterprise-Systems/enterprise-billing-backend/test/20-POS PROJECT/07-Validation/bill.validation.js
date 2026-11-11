/**
 * Bill / Invoice Validation Rules
 */

import { body } from 'express-validator';

export const billRules = [
  body('franchise_id').isInt({ min: 1 }).withMessage('Franchise ID is required'),
  body('items').isArray({ min: 1 }).withMessage('Items must be a non-empty array'),
  body('items.*.product_id').isInt({ min: 1 }).withMessage('Each item must have a valid product_id'),
  body('items.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be at least 1')
];
