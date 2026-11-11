import { Request, Response, NextFunction } from 'express';
import { AuditLog } from '../models/AuditLog';
import { logger } from '../utils/logger';

export const logAudit = (action: string, resource: string) => {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    res.on('finish', async () => {
      // Only log successful or sensitive mutating actions
      if (res.statusCode >= 200 && res.statusCode < 400) {
        try {
          await AuditLog.create({
            actorId: req.user?._id,
            actorRole: req.user?.role,
            action,
            resource,
            resourceId: req.params.id || req.body?.id || req.body?.sessionId || req.body?.userId,
            ipAddress: req.ip || req.socket.remoteAddress,
            deviceId: req.headers['x-device-id'] as string || req.user?.deviceId,
            metadata: {
              method: req.method,
              path: req.originalUrl,
              statusCode: res.statusCode,
              bodyParams: Object.keys(req.body || {}).filter(k => !['password', 'passwordHash', 'refreshToken'].includes(k))
            },
            timestamp: new Date()
          });
        } catch (err) {
          logger.error('Failed to write audit log', { err });
        }
      }
    });
    next();
  };
};
