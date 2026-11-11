import express from 'express';
import { register, login, getProfile } from '../controllers/authController.js';
import { validateRegister, validateLogin } from '../validation/authValidation.js';
import { verifyToken } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/register', validateRegister, register);
router.post('/login', validateLogin, login);
router.get('/profile', verifyToken, getProfile);

export default router;
