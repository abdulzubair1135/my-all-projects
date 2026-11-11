const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

// List circle contacts & conversations
router.get('/contacts', chatController.getContacts);

// Quick care item catalog for in-chat sharing
router.get('/quick-items', chatController.getQuickCareItems);

// Message thread for a specific connection
router.get('/messages/:connection_id', chatController.getMessages);

// Delete specific message
router.delete('/messages/:messageId', chatController.deleteMessage);

// Send text message
router.post('/send', chatController.sendMessage);

// Send or request a care / medical item in chat
router.post('/send-item', chatController.sendCareItem);

// Social User Search & Follow/Following & Tagging
router.get('/users/search', chatController.searchUsers);
router.post('/users/follow', chatController.followUser);
router.post('/users/unfollow', chatController.unfollowUser);
router.get('/users/:userId/social-stats', chatController.getUserSocialStats);
router.get('/users/:userId/followers', chatController.getFollowers);
router.get('/users/:userId/following', chatController.getFollowing);
router.post('/set-tag', chatController.setContactTag);
router.delete('/connections/:connection_id', chatController.deleteContact);

module.exports = router;
