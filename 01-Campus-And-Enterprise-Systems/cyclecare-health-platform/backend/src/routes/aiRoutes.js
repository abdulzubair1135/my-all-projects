const express = require('express');
const router = express.Router();
const aiController = require('../controllers/aiController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);
router.post('/chat', aiController.chatWithAI);

module.exports = router;
