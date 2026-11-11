import { Router, Request, Response } from 'express';
import { Hospital } from '../models/Hospital.js';
import { broadcastEvent } from '../sockets/socket.js';
import { requireAuth, requireRole, AuthRequest } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const hospitals = await Hospital.find().sort({ availableBeds: -1 });
    res.json({ success: true, data: hospitals });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.patch('/:id', requireAuth, requireRole(['HOSPITAL', 'ADMIN', 'SUPER_ADMIN', 'GOVERNMENT']), async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const {
      availableBeds,
      totalBeds,
      availableICUBeds,
      icuBeds,
      availableAmbulances,
      ambulances,
      emergencyStatus,
      bloodAvailability
    } = req.body;

    const hospital = await Hospital.findById(id);
    if (!hospital) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'Hospital record not found.' } });
      return;
    }

    if (availableBeds !== undefined) hospital.availableBeds = Number(availableBeds);
    if (totalBeds !== undefined) hospital.totalBeds = Number(totalBeds);
    if (availableICUBeds !== undefined) hospital.availableICUBeds = Number(availableICUBeds);
    if (icuBeds !== undefined) hospital.icuBeds = Number(icuBeds);
    if (availableAmbulances !== undefined) hospital.availableAmbulances = Number(availableAmbulances);
    if (ambulances !== undefined) hospital.ambulances = Number(ambulances);
    if (emergencyStatus) hospital.emergencyStatus = emergencyStatus;
    if (bloodAvailability) hospital.bloodAvailability = bloodAvailability;
    hospital.updatedBy = req.user?._id;

    await hospital.save();
    broadcastEvent('hospital:updated', hospital);

    res.json({ success: true, message: 'Hospital resources updated successfully.', data: hospital });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
