import { Router } from 'express';
import { LeaveController } from '../controllers/leave.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', LeaveController.getLeaves);

router.post(
  '/',
  requireRoles(UserRole.STUDENT),
  logAudit('SUBMIT_LEAVE_REQUEST', 'LeaveRequest'),
  LeaveController.submitLeave
);

router.patch(
  '/:id/review',
  requireRoles(UserRole.FACULTY, UserRole.PRINCIPAL, UserRole.SUPER_ADMIN),
  logAudit('REVIEW_LEAVE_REQUEST', 'LeaveRequest'),
  LeaveController.reviewLeave
);

export const leaveRoutes = router;
