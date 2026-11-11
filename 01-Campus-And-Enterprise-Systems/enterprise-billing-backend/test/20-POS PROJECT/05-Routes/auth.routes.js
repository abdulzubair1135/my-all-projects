/**
 * POS Auth Routes
 */

import express from 'express';
import { register, login } from '../04-Controllers/auth.controller.js';
import { registerRules, loginRules } from '../07-Validation/auth.validation.js';

const router = express.Router();

router.post('/register', registerRules, register);
router.post('/login', loginRules, login);

export default router;
