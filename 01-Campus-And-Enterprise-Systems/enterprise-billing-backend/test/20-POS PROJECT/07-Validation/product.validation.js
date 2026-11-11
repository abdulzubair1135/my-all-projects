/**
 * Product Validation Rules
 */

import { body } from 'express-validator';

export const productRules = [
  body('franchise_id').isInt({ min: 1 }).withMessage('Valid franchise ID is required'),
  body('name').trim().notEmpty().withMessage('Product name is required'),
  body('category').trim().notEmpty().withMessage('Category is required'),
  body('price').isFloat({ min: 0.01 }).withMessage('Price must be greater than 0'),
  body('stock').isInt({ min: 0 }).withMessage('Stock must be a non-negative integer')
];
