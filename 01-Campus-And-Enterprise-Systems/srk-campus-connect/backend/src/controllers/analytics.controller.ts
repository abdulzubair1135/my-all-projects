import { Request, Response, NextFunction } from 'express';
import { AnalyticsService } from '../services/analytics.service';
import { ResponseUtil } from '../utils/response';

export class AnalyticsController {
  static async getAttendanceAnalytics(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = await AnalyticsService.getAttendanceAnalytics();
      ResponseUtil.success(res, data, 'Attendance analytics retrieved');
    } catch (error: any) {
      next(error);
    }
  }

  static async getPresenceDistribution(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = await AnalyticsService.getPresenceDistribution();
      ResponseUtil.success(res, data, 'Presence distribution metrics retrieved');
    } catch (error: any) {
      next(error);
    }
  }

  static async getRoomAnalytics(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = await AnalyticsService.getRoomAnalytics();
      ResponseUtil.success(res, data, 'Room occupancy analytics retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
