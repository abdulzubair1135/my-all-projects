import { Router } from 'express';
import { 
  sendOtp, 
  verifyOtp, 
  registerWithOtp, 
  login, 
  getMe, 
  requestPasswordResetOtp, 
  changePasswordWithOtp 
} from '../controllers/AuthController.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

router.post('/send-otp', sendOtp);
router.post('/verify-otp', verifyOtp);
router.post('/register', registerWithOtp);
router.post('/signup', registerWithOtp);
router.post('/login', login);
router.post('/request-password-reset', requestPasswordResetOtp);
router.post('/change-password', changePasswordWithOtp);
router.get('/me', requireAuth, getMe);

export default router;
