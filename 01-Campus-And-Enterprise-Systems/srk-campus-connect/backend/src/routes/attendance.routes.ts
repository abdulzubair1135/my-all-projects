import { Router } from 'express';
import { AttendanceController } from '../controllers/attendance.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

// Student Identity QR
router.get('/student-qr', requireRoles(UserRole.STUDENT), AttendanceController.getStudentIdentityQr);

// Faculty direct scan of student QR
router.post(
  '/verify-student',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  logAudit('VERIFY_STUDENT_QR', 'Attendance'),
  AttendanceController.verifyStudentQr
);

// Faculty / Admin manual override
router.post(
  '/override',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('MANUAL_ATTENDANCE_OVERRIDE', 'Attendance'),
  AttendanceController.manualOverride
);

// Attendance queries
router.get('/session/:sessionId', AttendanceController.getSessionAttendance);
router.get('/student/history', AttendanceController.getStudentHistory);

export const attendanceRoutes = router;
