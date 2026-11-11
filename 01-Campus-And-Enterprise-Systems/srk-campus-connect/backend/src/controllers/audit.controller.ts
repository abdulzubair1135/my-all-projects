import { Request, Response, NextFunction } from 'express';
import { AuditLog } from '../models/AuditLog';
import { ResponseUtil } from '../utils/response';

export class AuditController {
  static async getAuditLogs(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { action, resource, limit } = req.query;
      const query: any = {};
      if (action) query.action = action;
      if (resource) query.resource = resource;

      const logs = await AuditLog.find(query)
        .populate('actorId', 'name email role')
        .sort({ timestamp: -1 })
        .limit(limit ? Number(limit) : 100);

      ResponseUtil.success(res, logs, 'Audit logs retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
