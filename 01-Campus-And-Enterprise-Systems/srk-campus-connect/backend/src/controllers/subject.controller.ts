import { Request, Response, NextFunction } from 'express';
import { SubjectService } from '../services/subject.service';
import { ResponseUtil } from '../utils/response';

export class SubjectController {
  static async createSubject(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { name, code, departmentId, semester, credits } = req.body;
      if (!name || !code || !departmentId || !semester) {
        ResponseUtil.error(res, 'name, code, departmentId, and semester are required', 400);
        return;
      }
      const subject = await SubjectService.createSubject({
        name,
        code,
        departmentId,
        semester: Number(semester),
        credits: credits ? Number(credits) : undefined
      });
      ResponseUtil.success(res, subject, 'Subject created successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async getSubjects(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId, semester } = req.query;
      const subjects = await SubjectService.getSubjects({
        departmentId: departmentId as string,
        semester: semester ? Number(semester) : undefined
      });
      ResponseUtil.success(res, subjects, 'Subjects retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getSubjectById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const subject = await SubjectService.getSubjectById(req.params.id);
      if (!subject) {
        ResponseUtil.error(res, 'Subject not found', 404);
        return;
      }
      ResponseUtil.success(res, subject, 'Subject retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updateSubject(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const subject = await SubjectService.updateSubject(req.params.id, req.body);
      if (!subject) {
        ResponseUtil.error(res, 'Subject not found', 404);
        return;
      }
      ResponseUtil.success(res, subject, 'Subject updated successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async deleteSubject(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const subject = await SubjectService.deleteSubject(req.params.id);
      if (!subject) {
        ResponseUtil.error(res, 'Subject not found', 404);
        return;
      }
      ResponseUtil.success(res, { id: req.params.id }, 'Subject deactivated successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
