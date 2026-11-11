/**
 * Franchise Routes
 */

import express from 'express';
import { getFranchises, getFranchiseById, createFranchise } from '../04-Controllers/franchise.controller.js';
import { authMiddleware } from '../06-Middleware/auth.middleware.js';

const router = express.Router();

router.get('/', getFranchises);
router.get('/:id', getFranchiseById);
router.post('/', authMiddleware, createFranchise);

export default router;
