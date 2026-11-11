import { Router } from 'express';
import { syncBatch, relayUpload } from '../controllers/SyncController.js';

const router = Router();

router.post('/sync', syncBatch);
router.post('/relay', relayUpload);

export default router;
