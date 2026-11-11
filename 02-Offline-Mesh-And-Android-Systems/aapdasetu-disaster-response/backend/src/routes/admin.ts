import { Router, Request, Response } from 'express';
import { User } from '../models/User.js';
import { AuditLog } from '../models/AuditLog.js';
import { requireAuth, requireRole } from '../middleware/auth.js';

const router = Router();

router.get('/users', requireAuth, requireRole(['ADMIN', 'SUPER_ADMIN']), async (req: Request, res: Response): Promise<void> => {
  try {
    const users = await User.find().select('-passwordHash').sort({ createdAt: -1 });
    res.json({ success: true, data: users });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.patch('/users/:id', requireAuth, requireRole(['ADMIN', 'SUPER_ADMIN']), async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { role, status } = req.body;
    const user = await User.findById(id);
    if (!user) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'User not found.' } });
      return;
    }
    if (role) user.role = role;
    if (status) user.status = status;
    await user.save();
    res.json({ success: true, message: 'User updated.', data: user });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.get('/audit-logs', requireAuth, requireRole(['ADMIN', 'SUPER_ADMIN', 'GOVERNMENT']), async (req: Request, res: Response): Promise<void> => {
  try {
    const logs = await AuditLog.find().sort({ timestamp: -1 }).limit(200);
    res.json({ success: true, data: logs });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
