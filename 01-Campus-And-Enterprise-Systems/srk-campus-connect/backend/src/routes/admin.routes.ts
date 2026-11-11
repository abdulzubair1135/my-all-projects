import { Router } from 'express';
import { AdminController } from '../controllers/admin.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);
router.use(requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL));

router.get('/search', AdminController.searchCampus);
router.get('/overview', AdminController.getCampusOverview);

export const adminRoutes = router;
