import { LeaveRequest, ILeaveRequest } from '../models/LeaveRequest';
import { Student } from '../models/Student';
import { Notification } from '../models/Notification';
import { LeaveRequestStatus } from '../constants/enums';

export class LeaveService {
  /**
   * Student submits a leave application
   */
  static async submitLeaveRequest(data: {
    studentId: string;
    fromDate: Date;
    toDate: Date;
    reason: string;
  }): Promise<ILeaveRequest> {
    return await LeaveRequest.create({
      studentId: data.studentId,
      fromDate: data.fromDate,
      toDate: data.toDate,
      reason: data.reason,
      status: LeaveRequestStatus.PENDING
    });
  }

  /**
   * Faculty/Admin approves or rejects student leave
   */
  static async reviewLeaveRequest(data: {
    leaveId: string;
    reviewerUserId: string;
    status: LeaveRequestStatus;
    reviewNotes?: string;
  }): Promise<ILeaveRequest | null> {
    const leave = await LeaveRequest.findById(data.leaveId).populate({
      path: 'studentId',
      populate: { path: 'userId', select: 'name email' }
    });

    if (!leave) {
      throw new Error('Leave request not found');
    }

    leave.status = data.status;
    leave.reviewedBy = data.reviewerUserId as any;
    if (data.reviewNotes) leave.reviewNotes = data.reviewNotes;
    await leave.save();

    // Send notification to student
    const studentUser = (leave.studentId as any)?.userId;
    if (studentUser) {
      const title = data.status === LeaveRequestStatus.APPROVED ? 'Leave Request Approved' : 'Leave Request Rejected';
      const body = `Your leave application from ${leave.fromDate.toLocaleDateString()} to ${leave.toDate.toLocaleDateString()} has been ${data.status.toLowerCase()}.`;

      await Notification.create({
        recipientId: studentUser._id,
        title,
        body,
        type: 'LEAVE_STATUS',
        payload: { leaveId: leave._id, status: data.status }
      });
    }

    return leave;
  }

  /**
   * Get student's leave requests
   */
  static async getStudentLeaves(studentId: string): Promise<ILeaveRequest[]> {
    return await LeaveRequest.find({ studentId }).sort({ createdAt: -1 });
  }

  /**
   * Get all pending leave requests for faculty/admin review
   */
  static async getAllLeaves(departmentId?: string): Promise<ILeaveRequest[]> {
    return await LeaveRequest.find()
      .populate({
        path: 'studentId',
        populate: [
          { path: 'userId', select: 'name email' },
          { path: 'departmentId', select: 'name code' }
        ]
      })
      .sort({ createdAt: -1 });
  }
}
