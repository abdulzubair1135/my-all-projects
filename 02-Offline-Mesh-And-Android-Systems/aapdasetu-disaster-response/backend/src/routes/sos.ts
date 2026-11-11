import { Router } from 'express';
import {
  createSOS,
  getAllSOS,
  getSOSById,
  updateStatus,
  verifySOS,
  assignRescueTeam,
  getSOSStats
} from '../controllers/SOSController.js';
import { requireAuth, requireRole } from '../middleware/auth.js';

const router = Router();

router.get('/stats/summary', getSOSStats);
router.post('/', createSOS);
router.get('/', getAllSOS);
router.get('/:id', getSOSById);
router.patch('/:id/status', updateStatus);
router.post('/:id/verify', requireAuth, requireRole(['GOVERNMENT', 'ADMIN', 'SUPER_ADMIN']), verifySOS);
router.post('/:id/assign', requireAuth, requireRole(['GOVERNMENT', 'ADMIN', 'SUPER_ADMIN', 'RESCUE']), assignRescueTeam);

export default router;
