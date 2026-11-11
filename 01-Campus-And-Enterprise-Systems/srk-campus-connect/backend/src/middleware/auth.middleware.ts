import { Request, Response, NextFunction } from 'express';
import { JwtUtil, JwtPayload } from '../security/jwt.util';
import { ResponseUtil } from '../utils/response';
import { User } from '../models/User';

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload & { _id: string };
    }
  }
}

export const authenticateJwt = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      ResponseUtil.error(res, 'Authentication token missing or malformed', 401);
      return;
    }

    const token = authHeader.split(' ')[1];
    const payload = JwtUtil.verifyAccessToken(token);

    const user = await User.findById(payload.sub).select('+isActive');
    if (!user || !user.isActive) {
      ResponseUtil.error(res, 'User account not found or suspended', 401);
      return;
    }

    req.user = {
      ...payload,
      _id: payload.sub
    };

    next();
  } catch (error: any) {
    if (error.name === 'TokenExpiredError') {
      ResponseUtil.error(res, 'Authentication token expired', 401);
      return;
    }
    ResponseUtil.error(res, 'Invalid authentication token', 401);
  }
};
