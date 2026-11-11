import express from 'express';
import { register, login, getProfile, updateAvatar } from '../controllers/authController.js';
import { validateRegister, validateLogin } from '../validation/authValidation.js';
import { verifyToken } from '../middleware/authMiddleware.js';
import { upload } from '../middleware/uploadMiddleware.js';

const router = express.Router();

router.post('/register', validateRegister, register);
router.post('/login', validateLogin, login);
router.get('/profile', verifyToken, getProfile);
router.post('/avatar', verifyToken, upload.single('avatar'), updateAvatar);

export default router;
