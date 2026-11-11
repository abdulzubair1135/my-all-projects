import { Router } from 'express';
import { FacultyController } from '../controllers/faculty.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', FacultyController.getAllFaculty);
router.get('/:id', FacultyController.getFacultyById);

router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_FACULTY', 'Faculty'),
  FacultyController.createFaculty
);

router.patch(
  '/:id/status',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL, UserRole.FACULTY),
  logAudit('UPDATE_FACULTY_STATUS', 'Faculty'),
  FacultyController.updateStatus
);

router.patch(
  '/:id/presence',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL, UserRole.FACULTY),
  logAudit('UPDATE_FACULTY_PRESENCE', 'Faculty'),
  FacultyController.updatePresence
);

export const facultyRoutes = router;
