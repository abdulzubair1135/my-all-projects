import { Router } from 'express';
import { SessionController } from '../controllers/session.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

// Active class check (for students and faculty)
router.get('/current', SessionController.getCurrentClass);
router.get('/:sessionId', SessionController.getSessionDetails);

// Faculty operations
router.post(
  '/start',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  logAudit('START_CLASS_SESSION', 'ClassSession'),
  SessionController.startClass
);

router.get(
  '/:sessionId/qr',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  SessionController.getRollingQr
);

router.post(
  '/:sessionId/end',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  logAudit('END_CLASS_SESSION', 'ClassSession'),
  SessionController.endClass
);

export const sessionRoutes = router;
