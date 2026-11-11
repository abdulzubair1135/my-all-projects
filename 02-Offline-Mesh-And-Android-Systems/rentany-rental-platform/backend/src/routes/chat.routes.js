import { Router } from 'express';
import { chatController } from '../controllers/chat.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { upload } from '../middleware/upload.middleware.js';

const router = Router();

router.get('/conversations', protect, chatController.getConversations);
router.get('/messages/:conversationId', protect, chatController.getMessages);

// Send message with optional file upload
router.post(
  '/messages',
  protect,
  upload.single('attachment'),
  chatController.sendMessage
);

export default router;
