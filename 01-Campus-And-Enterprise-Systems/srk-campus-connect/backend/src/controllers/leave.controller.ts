import { Request, Response, NextFunction } from 'express';
import { LeaveService } from '../services/leave.service';
import { Student } from '../models/Student';
import { ResponseUtil } from '../utils/response';
import { UserRole } from '../constants/enums';

export class LeaveController {
  static async submitLeave(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const student = await Student.findOne({ userId: req.user?._id });
      if (!student) {
        ResponseUtil.error(res, 'Student profile not found', 404);
        return;
      }

      const { fromDate, toDate, reason } = req.body;
      if (!fromDate || !toDate || !reason) {
        ResponseUtil.error(res, 'fromDate, toDate, and reason are required', 400);
        return;
      }

      const leave = await LeaveService.submitLeaveRequest({
        studentId: student._id.toString(),
        fromDate: new Date(fromDate),
        toDate: new Date(toDate),
        reason
      });

      ResponseUtil.success(res, leave, 'Leave application submitted successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async reviewLeave(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { status, reviewNotes } = req.body;
      if (!status) {
        ResponseUtil.error(res, 'status is required', 400);
        return;
      }

      const leave = await LeaveService.reviewLeaveRequest({
        leaveId: req.params.id,
        reviewerUserId: req.user?._id as string,
        status,
        reviewNotes
      });

      ResponseUtil.success(res, leave, 'Leave application review updated');
    } catch (error: any) {
      next(error);
    }
  }

  static async getLeaves(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      if (req.user?.role === UserRole.STUDENT) {
        const student = await Student.findOne({ userId: req.user._id });
        if (!student) {
          ResponseUtil.error(res, 'Student profile not found', 404);
          return;
        }
        const leaves = await LeaveService.getStudentLeaves(student._id.toString());
        ResponseUtil.success(res, leaves, 'Student leaves retrieved');
        return;
      }

      const allLeaves = await LeaveService.getAllLeaves();
      ResponseUtil.success(res, allLeaves, 'All campus leave requests');
    } catch (error: any) {
      next(error);
    }
  }
}
