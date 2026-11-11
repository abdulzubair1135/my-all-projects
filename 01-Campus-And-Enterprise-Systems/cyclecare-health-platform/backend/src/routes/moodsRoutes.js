const express = require('express');
const router = express.Router();
const moodsController = require('../controllers/moodsController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', moodsController.getMoods);
router.post('/log', moodsController.logMood);
router.get('/history', moodsController.getMoodHistory);

module.exports = router;
