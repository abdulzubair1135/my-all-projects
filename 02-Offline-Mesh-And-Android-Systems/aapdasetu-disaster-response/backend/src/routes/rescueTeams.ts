import { Router, Request, Response } from 'express';
import { RescueTeam } from '../models/RescueTeam.js';
import { broadcastEvent } from '../sockets/socket.js';
import { requireAuth, requireRole } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const teams = await RescueTeam.find().populate('currentAssignment');
    res.json({ success: true, data: teams });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/', requireAuth, requireRole(['GOVERNMENT', 'ADMIN', 'SUPER_ADMIN']), async (req: Request, res: Response): Promise<void> => {
  try {
    const { name, contactNumber, teamType, membersCount, vehicle, latitude, longitude } = req.body;
    const team = await RescueTeam.create({
      name,
      contactNumber,
      teamType: teamType || 'NDRF',
      membersCount: Number(membersCount) || 4,
      vehicle: vehicle || 'Rescue Van',
      location: {
        type: 'Point',
        coordinates: [Number(longitude || 72.5714), Number(latitude || 23.0225)]
      },
      status: 'AVAILABLE'
    });
    res.status(201).json({ success: true, message: 'Rescue team created.', data: team });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/:id/location', async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { latitude, longitude } = req.body;

    const team = await RescueTeam.findById(id);
    if (!team) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'Team not found.' } });
      return;
    }

    team.location = {
      type: 'Point',
      coordinates: [Number(longitude), Number(latitude)]
    };
    team.lastSeen = new Date();
    await team.save();

    broadcastEvent('rescue:location_updated', {
      teamId: team._id,
      name: team.name,
      location: team.location,
      status: team.status
    });

    res.json({ success: true, message: 'Location updated.' });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
