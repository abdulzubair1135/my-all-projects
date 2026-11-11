import { Router } from 'express';
import { StudentController } from '../controllers/student.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', StudentController.getStudents);
router.get('/enrollment/:enrollmentNo', StudentController.getStudentByEnrollmentNo);
router.get('/:id', StudentController.getStudentById);

router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_STUDENT', 'Student'),
  StudentController.createStudent
);

export const studentRoutes = router;
