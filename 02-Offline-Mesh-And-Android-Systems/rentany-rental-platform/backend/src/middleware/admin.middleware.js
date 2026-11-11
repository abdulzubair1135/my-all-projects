import { AppError } from './error.middleware.js';

export const adminOnly = (req, res, next) => {
  if (!req.user) {
    return next(new AppError('Authentication required.', 401));
  }
  
  if (req.user.role !== 'admin' && req.user.role !== 'super_admin') {
    return next(new AppError('Forbidden. Administrative access is required to access this resource.', 403));
  }
  
  next();
};

export const superAdminOnly = (req, res, next) => {
  if (!req.user) {
    return next(new AppError('Authentication required.', 401));
  }
  
  if (req.user.role !== 'super_admin') {
    return next(new AppError('Forbidden. Super administrative access is required to access this resource.', 403));
  }
  
  next();
};
