const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');

router.get('/chat/groups', chatController.getGroups);
router.post('/chat/groups', chatController.createGroup);
router.get('/chat/channels', chatController.getChannels);
router.get('/chat/messages', chatController.getMessages);
router.post('/chat/messages', chatController.sendMessage);
router.post('/chat/message', chatController.sendMessage);
router.post('/chat/messages/seen', chatController.markMessagesSeen);
router.post('/chat/messages/:id/react', chatController.reactMessage);

module.exports = router;
