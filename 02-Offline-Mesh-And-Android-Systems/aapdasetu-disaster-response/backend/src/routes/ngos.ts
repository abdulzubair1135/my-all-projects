import { Router, Request, Response } from 'express';
import { NGO } from '../models/NGO.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const ngos = await NGO.find();
    res.json({ success: true, data: ngos });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;
