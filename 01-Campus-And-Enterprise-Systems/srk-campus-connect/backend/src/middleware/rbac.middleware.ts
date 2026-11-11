import { Request, Response, NextFunction } from 'express';
import { UserRole } from '../constants/enums';
import { ResponseUtil } from '../utils/response';

export const requireRoles = (...allowedRoles: UserRole[]) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user) {
      ResponseUtil.error(res, 'Unauthenticated user', 401);
      return;
    }

    if (!allowedRoles.includes(req.user.role)) {
      ResponseUtil.error(res, `Forbidden: Requires one of roles [${allowedRoles.join(', ')}]`, 403);
      return;
    }

    next();
  };
};
