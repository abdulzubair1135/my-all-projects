import { Request, Response, NextFunction } from 'express';
import { AttendanceService } from '../services/attendance.service';
import { Student } from '../models/Student';
import { Faculty } from '../models/Faculty';
import { ResponseUtil } from '../utils/response';
import { UserRole } from '../constants/enums';

export class AttendanceController {
  static async getStudentIdentityQr(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      if (req.user?.role !== UserRole.STUDENT) {
        ResponseUtil.error(res, 'Only students can generate identity QR', 403);
        return;
      }

      const student = await Student.findOne({ userId: req.user._id });
      if (!student) {
        ResponseUtil.error(res, 'Student profile not found', 404);
        return;
      }

      const qrData = AttendanceService.generateStudentIdentityQr(student._id.toString(), student.enrollmentNo);
      ResponseUtil.success(res, qrData, 'Student identity QR generated successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async verifyStudentQr(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const faculty = await Faculty.findOne({ userId: req.user?._id });
      if (!faculty) {
        ResponseUtil.error(res, 'Faculty profile not found', 404);
        return;
      }

      const { sessionId, studentQrString } = req.body;
      if (!sessionId || !studentQrString) {
        ResponseUtil.error(res, 'sessionId and studentQrString are required', 400);
        return;
      }

      const attendance = await AttendanceService.verifyStudentByQr(sessionId, studentQrString, faculty._id.toString());
      ResponseUtil.success(res, attendance, 'Student verified and marked present', 201);
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Student verification failed', 400);
    }
  }

  static async manualOverride(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { sessionId, studentId, status, notes } = req.body;
      if (!sessionId || !studentId || !status) {
        ResponseUtil.error(res, 'sessionId, studentId, and status are required', 400);
        return;
      }

      const updated = await AttendanceService.manualOverride({
        sessionId,
        studentId,
        status,
        verifiedBy: req.user?._id as string,
        notes
      });

      ResponseUtil.success(res, updated, 'Attendance override recorded successfully');
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Override failed', 400);
    }
  }

  static async getSessionAttendance(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const records = await AttendanceService.getSessionAttendance(req.params.sessionId);
      ResponseUtil.success(res, records, 'Session attendance retrieved');
    } catch (error: any) {
      next(error);
    }
  }

  static async getStudentHistory(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      let studentId = req.query.studentId as string;

      if (req.user?.role === UserRole.STUDENT) {
        const student = await Student.findOne({ userId: req.user._id });
        if (!student) {
          ResponseUtil.error(res, 'Student profile not found', 404);
          return;
        }
        studentId = student._id.toString();
      }

      if (!studentId) {
        ResponseUtil.error(res, 'studentId is required', 400);
        return;
      }

      const history = await AttendanceService.getStudentAttendanceHistory(studentId);
      ResponseUtil.success(res, history, 'Student attendance history retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
