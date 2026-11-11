const express = require('express');
const router = express.Router();
const notificationController = require('../controllers/notificationController');

// Notifications
router.get('/notifications', notificationController.getNotifications);
router.patch('/notifications/:id/read', notificationController.markNotificationRead);
router.post('/notifications/mark-all-read', notificationController.markAllRead);
router.post('/notifications/send-push', notificationController.sendPush);

// Broadcast
router.post('/broadcast/send', notificationController.handleBroadcastSend);
router.post('/fcm/broadcast', notificationController.handleBroadcastSend);
router.get('/broadcast/history', notificationController.getBroadcastHistory);

module.exports = router;
