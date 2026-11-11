import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { User, IUser } from '../models/User.js';
import { AuditLog } from '../models/AuditLog.js';

export interface AuthRequest extends Request {
  user?: IUser;
  deviceId?: string;
}

export const requireAuth = async (req: AuthRequest, res: Response, next: NextFunction): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: 'Authentication required. No bearer token provided.' }
      });
      return;
    }

    const token = authHeader.split(' ')[1];
    const secret = process.env.JWT_SECRET || 'aapdasetu_jwt_secret_change_in_production_2026_secure';
    const decoded = jwt.verify(token, secret) as { id: string; role: string; deviceId?: string };

    const user = await User.findById(decoded.id);
    if (!user) {
      res.status(401).json({
        success: false,
        error: { code: 'USER_NOT_FOUND', message: 'User session is invalid or user has been removed.' }
      });
      return;
    }

    req.user = user;
    req.deviceId = decoded.deviceId || (req.headers['x-device-id'] as string);
    next();
  } catch (error) {
    res.status(401).json({
      success: false,
      error: { code: 'TOKEN_INVALID', message: 'Invalid or expired authentication token.' }
    });
  }
};

export const requireRole = (allowedRoles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: 'Authentication required.' }
      });
      return;
    }

    if (req.user.role === 'SUPER_ADMIN' || allowedRoles.includes(req.user.role)) {
      next();
      return;
    }

    res.status(403).json({
      success: false,
      error: {
        code: 'FORBIDDEN',
        message: `Access denied. Requires one of roles: [${allowedRoles.join(', ')}]. Current: ${req.user.role}`
      }
    });
  };
};

export const logAudit = async (
  req: AuthRequest,
  action: string,
  entityType: string,
  entityId?: string,
  metadata?: Record<string, any>
): Promise<void> => {
  try {
    await AuditLog.create({
      userId: req.user?._id,
      userName: req.user?.name,
      action,
      entityType,
      entityId,
      ipAddress: req.ip || req.socket.remoteAddress,
      deviceId: req.deviceId || (req.headers['x-device-id'] as string),
      metadata,
      timestamp: new Date()
    });
  } catch (err) {
    console.error('[AuditLog] Failed to record audit log:', err);
  }
};
