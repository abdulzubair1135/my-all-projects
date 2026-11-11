import { Router } from 'express';
import { AnalyticsController } from '../controllers/analytics.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);
router.use(requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL, UserRole.FACULTY));

router.get('/overview', AnalyticsController.getAttendanceAnalytics);
router.get('/presence', AnalyticsController.getPresenceDistribution);
router.get('/attendance-rates', AnalyticsController.getAttendanceAnalytics);
router.get('/presence-distribution', AnalyticsController.getPresenceDistribution);
router.get('/room-occupancy', AnalyticsController.getRoomAnalytics);

export const analyticsRoutes = router;
