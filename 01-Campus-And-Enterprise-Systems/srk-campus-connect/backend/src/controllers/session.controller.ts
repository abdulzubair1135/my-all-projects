import { Request, Response, NextFunction } from 'express';
import { SessionService } from '../services/session.service';
import { Faculty } from '../models/Faculty';
import { Student } from '../models/Student';
import { ResponseUtil } from '../utils/response';
import { UserRole } from '../constants/enums';

export class SessionController {
  static async startClass(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      if (req.user?.role !== UserRole.FACULTY && req.user?.role !== UserRole.SUPER_ADMIN) {
        ResponseUtil.error(res, 'Only faculty members can start a class session', 403);
        return;
      }

      const faculty = await Faculty.findOne({ userId: req.user._id });
      if (!faculty) {
        ResponseUtil.error(res, 'Faculty profile not found', 404);
        return;
      }

      const { timetableId, roomId, permanentRoomQr, subjectId } = req.body;
      if (!roomId) {
        ResponseUtil.error(res, 'roomId is required to start a class', 400);
        return;
      }

      const session = await SessionService.startSession({
        facultyId: faculty._id.toString(),
        timetableId,
        roomId,
        permanentRoomQr,
        subjectId
      });

      ResponseUtil.success(res, session, 'Class session started successfully', 201);
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Failed to start class session', 400);
    }
  }

  static async getCurrentClass(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      if (req.user?.role === UserRole.FACULTY) {
        const faculty = await Faculty.findOne({ userId: req.user._id });
        if (!faculty) {
          ResponseUtil.error(res, 'Faculty profile not found', 404);
          return;
        }
        const session = await SessionService.getCurrentSessionForFaculty(faculty._id.toString());
        ResponseUtil.success(res, session, session ? 'Active faculty class session' : 'No active class session');
        return;
      }

      if (req.user?.role === UserRole.STUDENT) {
        const student = await Student.findOne({ userId: req.user._id });
        if (!student) {
          ResponseUtil.error(res, 'Student profile not found', 404);
          return;
        }
        const session = await SessionService.getCurrentSessionForStudent({
          departmentId: student.departmentId.toString(),
          semester: student.semester,
          division: student.division,
          academicYear: student.academicYear
        });
        ResponseUtil.success(res, session, session ? 'Active student class session' : 'No active class session');
        return;
      }

      ResponseUtil.error(res, 'Invalid role for getCurrentClass', 400);
    } catch (error: any) {
      next(error);
    }
  }

  static async getRollingQr(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const faculty = await Faculty.findOne({ userId: req.user?._id });
      if (!faculty) {
        ResponseUtil.error(res, 'Faculty profile not found', 404);
        return;
      }

      const qrData = await SessionService.getRollingSessionQr(req.params.sessionId, faculty._id.toString());
      ResponseUtil.success(res, qrData, 'Rolling QR generated successfully');
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Failed to generate rolling QR', 400);
    }
  }

  static async endClass(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const faculty = await Faculty.findOne({ userId: req.user?._id });
      if (!faculty) {
        ResponseUtil.error(res, 'Faculty profile not found', 404);
        return;
      }

      const session = await SessionService.endSession(req.params.sessionId, faculty._id.toString());
      ResponseUtil.success(res, session, 'Class session ended successfully');
    } catch (error: any) {
      ResponseUtil.error(res, error.message || 'Failed to end class session', 400);
    }
  }

  static async getSessionDetails(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const session = await SessionService.getSessionBySessionId(req.params.sessionId);
      if (!session) {
        ResponseUtil.error(res, 'Class session not found', 404);
        return;
      }
      ResponseUtil.success(res, session, 'Class session details retrieved');
    } catch (error: any) {
      next(error);
    }
  }
}
