import { Request, Response, NextFunction } from 'express';
import { TimetableService } from '../services/timetable.service';
import { Student } from '../models/Student';
import { Faculty } from '../models/Faculty';
import { ResponseUtil } from '../utils/response';
import { UserRole } from '../constants/enums';

export class TimetableController {
  static async getStudentTimetable(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      let { departmentId, semester, division, academicYear, dayOfWeek } = req.query;

      // If requested by a student, automatically retrieve their registered cohort params
      if (req.user?.role === UserRole.STUDENT) {
        const student = await Student.findOne({ userId: req.user._id });
        if (!student) {
          ResponseUtil.error(res, 'Student profile not found', 404);
          return;
        }
        departmentId = student.departmentId.toString();
        semester = String(student.semester);
        division = student.division;
        academicYear = student.academicYear;
      }

      if (!departmentId || !semester || !division) {
        ResponseUtil.error(res, 'departmentId, semester, and division are required', 400);
        return;
      }

      const timetable = await TimetableService.getStudentTimetable({
        departmentId: departmentId as string,
        semester: Number(semester),
        division: division as string,
        academicYear: academicYear as string,
        dayOfWeek: dayOfWeek ? Number(dayOfWeek) : undefined
      });

      ResponseUtil.success(res, timetable, 'Student timetable retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getFacultyTimetable(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      let facultyId = req.query.facultyId as string;
      const dayOfWeek = req.query.dayOfWeek ? Number(req.query.dayOfWeek) : undefined;

      // If requested by faculty, automatically retrieve their assigned faculty ID
      if (req.user?.role === UserRole.FACULTY) {
        const faculty = await Faculty.findOne({ userId: req.user._id });
        if (!faculty) {
          ResponseUtil.error(res, 'Faculty profile not found', 404);
          return;
        }
        facultyId = faculty._id.toString();
      }

      if (!facultyId) {
        ResponseUtil.error(res, 'facultyId query parameter is required', 400);
        return;
      }

      const timetable = await TimetableService.getFacultyTimetable(facultyId, dayOfWeek);
      ResponseUtil.success(res, timetable, 'Faculty timetable retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getMasterTimetable(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId, semester, division, facultyId, roomId, dayOfWeek } = req.query;
      const timetable = await TimetableService.getMasterTimetable({
        departmentId: departmentId as string,
        semester: semester ? Number(semester) : undefined,
        division: division as string,
        facultyId: facultyId as string,
        roomId: roomId as string,
        dayOfWeek: dayOfWeek ? Number(dayOfWeek) : undefined
      });

      ResponseUtil.success(res, timetable, 'Master timetable retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async createSlot(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { departmentId, semester, division, subjectId, facultyId, roomId, dayOfWeek, startTime, endTime, academicYear } = req.body;
      if (!departmentId || !semester || !division || !subjectId || !facultyId || !roomId || !dayOfWeek || !startTime || !endTime || !academicYear) {
        ResponseUtil.error(res, 'All timetable slot parameters are required', 400);
        return;
      }

      const slot = await TimetableService.createSlot({
        departmentId,
        semester: Number(semester),
        division,
        subjectId,
        facultyId,
        roomId,
        dayOfWeek: Number(dayOfWeek),
        startTime,
        endTime,
        academicYear
      });

      ResponseUtil.success(res, slot, 'Timetable slot created successfully', 201);
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Failed to create timetable slot', 400);
    }
  }

  static async updateSlot(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const updated = await TimetableService.updateSlot(req.params.id, req.body);
      ResponseUtil.success(res, updated, 'Timetable slot updated successfully');
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Failed to update timetable slot', 400);
    }
  }

  static async deleteSlot(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const deleted = await TimetableService.deleteSlot(req.params.id);
      ResponseUtil.success(res, deleted, 'Timetable slot deactivated successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
