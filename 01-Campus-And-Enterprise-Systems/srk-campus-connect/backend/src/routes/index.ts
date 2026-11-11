import { Router, Request, Response } from 'express';
import { authRoutes } from './auth.routes';
import { deviceRoutes } from './device.routes';
import { departmentRoutes } from './department.routes';
import { subjectRoutes } from './subject.routes';
import { roomRoutes } from './room.routes';
import { facultyRoutes } from './faculty.routes';
import { studentRoutes } from './student.routes';
import { adminRoutes } from './admin.routes';
import { timetableRoutes } from './timetable.routes';
import { sessionRoutes } from './session.routes';
import { attendanceRoutes } from './attendance.routes';
import { syncRoutes } from './sync.routes';
import { presenceRoutes } from './presence.routes';
import { meetingRoutes } from './meeting.routes';
import { leaveRoutes } from './leave.routes';
import { analyticsRoutes } from './analytics.routes';
import { auditRoutes } from './audit.routes';
import { ResponseUtil } from '../utils/response';

const router = Router();

// Health Check
router.get('/health', (req: Request, res: Response) => {
  ResponseUtil.success(res, {
    status: 'healthy',
    timestamp: new Date(),
    uptime: process.uptime(),
    version: '1.0.0'
  }, 'Campus Coordination Backend API is operational');
});

router.use('/auth', authRoutes);
router.use('/devices', deviceRoutes);
router.use('/departments', departmentRoutes);
router.use('/subjects', subjectRoutes);
router.use('/rooms', roomRoutes);
router.use('/faculty', facultyRoutes);
router.use('/students', studentRoutes);
router.use('/admin', adminRoutes);
router.use('/timetable', timetableRoutes);
router.use('/classes', sessionRoutes);
router.use('/attendance', attendanceRoutes);
router.use('/sync', syncRoutes);
router.use('/presence', presenceRoutes);
router.use('/meetings', meetingRoutes);
router.use('/leaves', leaveRoutes);
router.use('/analytics', analyticsRoutes);
router.use('/audit', auditRoutes);

export const apiRoutes = router;
