const express = require('express');
const router = express.Router();
const remindersController = require('../controllers/remindersController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', remindersController.getReminders);
router.post('/', remindersController.createReminder);
router.put('/:id', remindersController.updateReminder);
router.patch('/:id', remindersController.updateReminder);
router.delete('/:id', remindersController.deleteReminder);

module.exports = router;
