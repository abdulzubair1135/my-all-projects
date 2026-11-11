import { body, validationResult } from 'express-validator';

export const validatePost = [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('slug').trim().notEmpty().withMessage('Slug is required'),
  body('content').trim().notEmpty().withMessage('Content is required'),
  body('author_name').trim().notEmpty().withMessage('Author name is required'),
  body('status').optional().isIn(['draft', 'published']).withMessage('Status must be draft or published'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', errors: errors.array().map(e => e.msg) });
    }
    next();
  }
];
