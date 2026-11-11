import { Router } from 'express';
import { TimetableController } from '../controllers/timetable.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

// Student & Faculty & Admin access
router.get('/student', TimetableController.getStudentTimetable);
router.get('/faculty', TimetableController.getFacultyTimetable);
router.get('/', TimetableController.getMasterTimetable);

// Admin-only mutation endpoints
router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_TIMETABLE_SLOT', 'Timetable'),
  TimetableController.createSlot
);

router.put(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('UPDATE_TIMETABLE_SLOT', 'Timetable'),
  TimetableController.updateSlot
);

router.delete(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('DELETE_TIMETABLE_SLOT', 'Timetable'),
  TimetableController.deleteSlot
);

export const timetableRoutes = router;
