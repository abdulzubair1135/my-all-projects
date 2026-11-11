import { Request, Response, NextFunction } from 'express';
import { FacultyService } from '../services/faculty.service';
import { ResponseUtil } from '../utils/response';
import { FacultyStatus } from '../constants/enums';

export class FacultyController {
  static async createFaculty(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { name, email, phone, password, employeeId, departmentId, designation, subjects } = req.body;
      if (!name || !email || !employeeId || !departmentId || !designation) {
        ResponseUtil.error(res, 'name, email, employeeId, departmentId, and designation are required', 400);
        return;
      }
      const result = await FacultyService.createFaculty({
        name,
        email,
        phone,
        password,
        employeeId,
        departmentId,
        designation,
        subjects
      });
      ResponseUtil.success(res, result, 'Faculty created successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async getAllFaculty(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId } = req.query;
      const faculty = await FacultyService.getAllFaculty(departmentId as string);
      ResponseUtil.success(res, faculty, 'Faculty list retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getFacultyById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const faculty = await FacultyService.getFacultyById(req.params.id);
      if (!faculty) {
        ResponseUtil.error(res, 'Faculty not found', 404);
        return;
      }
      ResponseUtil.success(res, faculty, 'Faculty details retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updateStatus(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { status } = req.body;
      if (!Object.values(FacultyStatus).includes(status)) {
        ResponseUtil.error(res, 'Invalid faculty status', 400);
        return;
      }

      // If faculty is modifying their own status or admin
      const facultyId = req.params.id;
      const updated = await FacultyService.updateStatus(facultyId, status);
      ResponseUtil.success(res, updated, 'Faculty status updated successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updatePresence(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { roomId, confidence } = req.body;
      if (!roomId || confidence === undefined) {
        ResponseUtil.error(res, 'roomId and confidence are required', 400);
        return;
      }
      const updated = await FacultyService.updatePresence(req.params.id, roomId, Number(confidence));
      ResponseUtil.success(res, updated, 'Faculty presence updated successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
