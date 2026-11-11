import { Router, Request, Response } from 'express';
import { Alert } from '../models/Alert.js';
import { broadcastEvent } from '../sockets/socket.js';
import { requireAuth, requireRole, AuthRequest } from '../middleware/auth.js';
import { sendEmergencyPushNotification } from '../services/firebaseService.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const alerts = await Alert.find({ active: true }).sort({ createdAt: -1 });
    res.json({ success: true, data: alerts });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const { title, message, type, severity, latitude, longitude, radiusKm, expiresAt, source } = req.body;
    if (!title || !message) {
      res.status(400).json({ success: false, error: { code: 'VALIDATION_ERROR', message: 'Title and message required.' } });
      return;
    }

    const alert = await Alert.create({
      title,
      message,
      type: type || 'GENERAL',
      severity: severity || 'WARNING',
      location: {
        type: 'Point',
        coordinates: [Number(longitude || 72.5714), Number(latitude || 23.0225)]
      },
      radiusKm: Number(radiusKm) || 15,
      source: source || 'GOVERNMENT',
      expiresAt: expiresAt ? new Date(expiresAt) : new Date(Date.now() + 24 * 60 * 60 * 1000),
      active: true
    });

    try {
      broadcastEvent('alert:new', alert);
      broadcastEvent('alert:broadcast', alert);
      sendEmergencyPushNotification(
        `🚨 ${alert.severity}: ${alert.title}`,
        alert.message,
        { alertId: alert._id.toString(), type: alert.type, severity: alert.severity }
      ).catch(() => {});
    } catch (ignored) {}

    res.status(201).json({ success: true, message: 'Emergency alert issued and broadcasted.', data: alert });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
