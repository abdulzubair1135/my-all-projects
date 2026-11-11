import { Router } from 'express';
import { SubjectController } from '../controllers/subject.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', SubjectController.getSubjects);
router.get('/:id', SubjectController.getSubjectById);

router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_SUBJECT', 'Subject'),
  SubjectController.createSubject
);

router.put(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('UPDATE_SUBJECT', 'Subject'),
  SubjectController.updateSubject
);

router.delete(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN),
  logAudit('DELETE_SUBJECT', 'Subject'),
  SubjectController.deleteSubject
);

export const subjectRoutes = router;
