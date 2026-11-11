import { Router } from 'express';
import { DeviceController } from '../controllers/device.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { logAudit } from '../middleware/audit.middleware';

const router = Router();

router.use(authenticateJwt);

router.post('/register', logAudit('DEVICE_REGISTER', 'Device'), DeviceController.registerDevice);
router.get('/my-devices', DeviceController.getMyDevices);

export const deviceRoutes = router;
