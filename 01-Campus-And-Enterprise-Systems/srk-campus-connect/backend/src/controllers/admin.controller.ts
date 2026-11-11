import { Request, Response, NextFunction } from 'express';
import { AdminService } from '../services/admin.service';
import { ResponseUtil } from '../utils/response';

export class AdminController {
  static async searchCampus(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { q } = req.query;
      if (!q || typeof q !== 'string') {
        ResponseUtil.error(res, 'Search query parameter "q" is required', 400);
        return;
      }
      const results = await AdminService.searchCampus(q);
      ResponseUtil.success(res, results, 'Campus search results');
    } catch (error: any) {
      next(error);
    }
  }

  static async getCampusOverview(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const overview = await AdminService.getCampusOverview();
      ResponseUtil.success(res, overview, 'Campus overview metrics retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
