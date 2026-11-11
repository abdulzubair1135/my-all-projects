import { Router } from 'express';
import { SyncController } from '../controllers/sync.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { syncRateLimiter } from '../middleware/rateLimiter.middleware';
import { logAudit } from '../middleware/audit.middleware';

const router = Router();

router.use(authenticateJwt);

// Offline sync batch ingestion (direct or via elected P2P gateway)
router.post(
  '/events',
  syncRateLimiter,
  logAudit('BATCH_OFFLINE_SYNC', 'PresenceEvent'),
  SyncController.ingestSyncEvents
);

export const syncRoutes = router;
