import { validationResult } from 'express-validator';
import { AppError } from './error.middleware.js';

export const validateRequest = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorArray = errors.array().map(err => ({
      field: err.path,
      message: err.msg
    }));
    return next(new AppError('Validation failed', 422, errorArray));
  }
  next();
};
