/**
 * Complete Validation Examples using express-validator
 * ES Module Format with Clean Error Responses
 */

import express from 'express';
import { body, param, query, validationResult } from 'express-validator';

const router = express.Router();

/**
 * Reusable Middleware to Handle Validation Errors
 */
export const checkValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation error occurred',
      errors: errors.array().map(err => ({
        field: err.path,
        message: err.msg
      }))
    });
  }
  next();
};

/**
 * 1. Body Validation Example (Create Student/User)
 * POST /api/validation/students
 */
export const validateCreateStudent = [
  body('name')
    .trim()
    .notEmpty().withMessage('Student name is required')
    .isLength({ min: 2, max: 50 }).withMessage('Name must be between 2 and 50 characters'),
  
  body('email')
    .trim()
    .notEmpty().withMessage('Email address is required')
    .isEmail().withMessage('Must be a valid email format')
    .normalizeEmail(),

  body('age')
    .notEmpty().withMessage('Age is required')
    .isInt({ min: 16, max: 100 }).withMessage('Age must be an integer between 16 and 100')
    .toInt(),

  body('course')
    .trim()
    .notEmpty().withMessage('Course is required')
    .isIn(['BCA', 'MCA', 'BTech', 'MTech']).withMessage('Invalid course name'),

  checkValidation
];

router.post('/students', validateCreateStudent, (req, res) => {
  const { name, email, age, course } = req.body;
  res.status(201).json({
    success: true,
    message: 'Student registered successfully',
    data: { name, email, age, course }
  });
});

/**
 * 2. Param Validation Example (Get Student by ID)
 * GET /api/validation/students/:id
 */
export const validateStudentId = [
  param('id')
    .exists().withMessage('ID parameter is required')
    .isInt({ min: 1 }).withMessage('ID must be a positive integer')
    .toInt(),
  checkValidation
];

router.get('/students/:id', validateStudentId, (req, res) => {
  const studentId = req.params.id;
  res.status(200).json({
    success: true,
    message: `Fetched details for student ID: ${studentId}`,
    data: { id: studentId, name: 'Rahul Sharma', course: 'BCA' }
  });
});

/**
 * 3. Query Validation Example (Filter & Paginate)
 * GET /api/validation/search?page=1&limit=10&search=rahul
 */
export const validateSearchQuery = [
  query('page')
    .optional()
    .isInt({ min: 1 }).withMessage('Page number must be >= 1')
    .toInt(),

  query('limit')
    .optional()
    .isInt({ min: 1, max: 50 }).withMessage('Limit must be between 1 and 50')
    .toInt(),

  query('search')
    .optional()
    .trim()
    .escape(),

  checkValidation
];

router.get('/search', validateSearchQuery, (req, res) => {
  const page = req.query.page || 1;
  const limit = req.query.limit || 10;
  const search = req.query.search || '';

  res.status(200).json({
    success: true,
    message: 'Query parameters processed successfully',
    data: { page, limit, search }
  });
});

export default router;
