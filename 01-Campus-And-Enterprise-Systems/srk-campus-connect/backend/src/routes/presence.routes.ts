import { Router } from 'express';
import { SyncController } from '../controllers/sync.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { logAudit } from '../middleware/audit.middleware';

const router = Router();

router.use(authenticateJwt);

// Direct single event ingestion
router.post(
  '/event',
  logAudit('INGEST_PRESENCE_EVENT', 'PresenceEvent'),
  SyncController.ingestSingleEvent
);

export const presenceRoutes = router;
