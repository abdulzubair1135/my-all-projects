import { Router, Request, Response } from 'express';
import { Shelter } from '../models/Shelter.js';
import { broadcastEvent } from '../sockets/socket.js';
import { requireAuth, requireRole } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const shelters = await Shelter.find().sort({ capacity: -1 });
    res.json({ success: true, data: shelters });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.patch('/:id', requireAuth, requireRole(['GOVERNMENT', 'NGO', 'ADMIN', 'SUPER_ADMIN']), async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { occupied, capacity, waterAvailable, foodAvailable, medicalAvailable, status } = req.body;

    const shelter = await Shelter.findById(id);
    if (!shelter) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'Shelter record not found.' } });
      return;
    }

    if (occupied !== undefined) shelter.occupied = Number(occupied);
    if (capacity !== undefined) shelter.capacity = Number(capacity);
    if (waterAvailable !== undefined) shelter.waterAvailable = Boolean(waterAvailable);
    if (foodAvailable !== undefined) shelter.foodAvailable = Boolean(foodAvailable);
    if (medicalAvailable !== undefined) shelter.medicalAvailable = Boolean(medicalAvailable);
    if (status) shelter.status = status;

    await shelter.save();
    broadcastEvent('shelter:updated', shelter);

    res.json({ success: true, message: 'Shelter updated successfully.', data: shelter });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
