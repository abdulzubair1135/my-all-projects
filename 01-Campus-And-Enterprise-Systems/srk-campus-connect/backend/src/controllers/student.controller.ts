import { Request, Response, NextFunction } from 'express';
import { StudentService } from '../services/student.service';
import { ResponseUtil } from '../utils/response';

export class StudentController {
  static async createStudent(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { name, email, phone, password, enrollmentNo, departmentId, semester, division, academicYear } = req.body;
      if (!name || !email || !enrollmentNo || !departmentId || !semester || !division || !academicYear) {
        ResponseUtil.error(res, 'All student enrollment fields are required', 400);
        return;
      }
      const result = await StudentService.createStudent({
        name,
        email,
        phone,
        password,
        enrollmentNo,
        departmentId,
        semester: Number(semester),
        division,
        academicYear
      });
      ResponseUtil.success(res, result, 'Student enrolled successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async getStudents(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId, semester, division, academicYear } = req.query;
      const students = await StudentService.getStudents({
        departmentId: departmentId as string,
        semester: semester ? Number(semester) : undefined,
        division: division as string,
        academicYear: academicYear as string
      });
      ResponseUtil.success(res, students, 'Student list retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getStudentById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const student = await StudentService.getStudentById(req.params.id);
      if (!student) {
        ResponseUtil.error(res, 'Student not found', 404);
        return;
      }
      ResponseUtil.success(res, student, 'Student details retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getStudentByEnrollmentNo(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const student = await StudentService.getStudentByEnrollmentNo(req.params.enrollmentNo);
      if (!student) {
        ResponseUtil.error(res, 'Student not found with this enrollment number', 404);
        return;
      }
      ResponseUtil.success(res, student, 'Student retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
