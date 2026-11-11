import { Router, Request, Response } from 'express';
import { Volunteer } from '../models/Volunteer.js';
import { requireAuth, AuthRequest } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const volunteers = await Volunteer.find().sort({ lastActive: -1 });
    res.json({ success: true, data: volunteers });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/register', requireAuth, async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { skills, vehicle, latitude, longitude } = req.body;
    let vol = await Volunteer.findOne({ userId: req.user?._id });
    if (!vol) {
      vol = await Volunteer.create({
        userId: req.user?._id,
        name: req.user?.name || 'Volunteer',
        phone: req.user?.phone || '',
        skills: skills || ['Search & Rescue', 'First Aid'],
        vehicle: vehicle || 'Bike',
        location: {
          type: 'Point',
          coordinates: [Number(longitude || 72.5714), Number(latitude || 23.0225)]
        },
        availability: 'AVAILABLE'
      });
    } else {
      if (skills) vol.skills = skills;
      if (vehicle) vol.vehicle = vehicle;
      if (latitude && longitude) {
        vol.location = { type: 'Point', coordinates: [Number(longitude), Number(latitude)] };
      }
      vol.lastActive = new Date();
      await vol.save();
    }
    res.json({ success: true, message: 'Volunteer profile updated.', data: vol });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
