/**
 * User Input Validation Rules using express-validator
 */

import { body, param } from 'express-validator';

// User Create / Update Validation Rules
export const userValidationRules = [
  body('name')
    .trim()
    .notEmpty().withMessage('Name is required')
    .isLength({ min: 2 }).withMessage('Name must be at least 2 characters long'),
  
  body('email')
    .trim()
    .notEmpty().withMessage('Email is required')
    .isEmail().withMessage('Please enter a valid email address'),
  
  body('age')
    .notEmpty().withMessage('Age is required')
    .isInt({ min: 1, max: 120 }).withMessage('Age must be a valid integer between 1 and 120'),
  
  body('city')
    .trim()
    .notEmpty().withMessage('City is required')
];

// User ID URL Parameter Validation Rule
export const idValidationRule = [
  param('id')
    .isInt({ min: 1 }).withMessage('User ID must be a positive integer')
];
