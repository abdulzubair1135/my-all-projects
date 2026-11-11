import { Router, Request, Response } from 'express';
import { Resource } from '../models/Resource.js';
import { ResourceRequest } from '../models/ResourceRequest.js';
import { requireAuth, requireRole } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const resources = await Resource.find();
    res.json({ success: true, data: resources });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/', requireAuth, requireRole(['GOVERNMENT', 'NGO', 'ADMIN', 'SUPER_ADMIN']), async (req: Request, res: Response): Promise<void> => {
  try {
    const { organizationName, type, quantity, unit, latitude, longitude } = req.body;
    const resource = await Resource.create({
      organizationName: organizationName || 'State Disaster Relief Reserve',
      type,
      quantity: Number(quantity),
      unit: unit || 'kits',
      location: {
        type: 'Point',
        coordinates: [Number(longitude || 72.5714), Number(latitude || 23.0225)]
      },
      availableQuantity: Number(quantity),
      reservedQuantity: 0
    });
    res.status(201).json({ success: true, message: 'Resource recorded.', data: resource });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.get('/requests', async (req: Request, res: Response): Promise<void> => {
  try {
    const requests = await ResourceRequest.find().sort({ createdAt: -1 });
    res.json({ success: true, data: requests });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/requests', async (req: Request, res: Response): Promise<void> => {
  try {
    const { requestedBy, resourceType, quantity, priority, latitude, longitude } = req.body;
    const request = await ResourceRequest.create({
      requestedBy: requestedBy || 'Relief Camp Area 4',
      resourceType,
      quantity: Number(quantity),
      priority: priority || 'HIGH',
      location: {
        type: 'Point',
        coordinates: [Number(longitude || 72.5714), Number(latitude || 23.0225)]
      },
      status: 'PENDING'
    });
    res.status(201).json({ success: true, message: 'Relief request created.', data: request });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
