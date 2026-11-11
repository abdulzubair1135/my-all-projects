/**
 * Bill / Invoice Routes
 */

import express from 'express';
import { getBills, getBillById, generateBill } from '../04-Controllers/bill.controller.js';
import { billRules } from '../07-Validation/bill.validation.js';
import { authMiddleware } from '../06-Middleware/auth.middleware.js';

const router = express.Router();

router.get('/', authMiddleware, getBills);
router.get('/:id', authMiddleware, getBillById);
router.post('/', authMiddleware, billRules, generateBill);

export default router;
