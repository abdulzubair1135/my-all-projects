import { Router } from 'express';
import { AuditController } from '../controllers/audit.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { UserRole } from '../constants/enums';

import { TelemetryService } from '../services/telemetry.service';
import { ResponseUtil } from '../utils/response';

const router = Router();

// Public Telemetry Snapshot for Control Panel
router.get('/telemetry', (req, res) => {
  const snapshot = TelemetryService.getDashboardSnapshot();
  ResponseUtil.success(res, snapshot, 'Telemetry snapshot retrieved');
});

router.use(authenticateJwt);
router.use(requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL));

router.get('/logs', AuditController.getAuditLogs);

export const auditRoutes = router;
