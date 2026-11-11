const express = require('express');
const router = express.Router();
const careKitController = require('../controllers/careKitController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', careKitController.getCareKits);
router.post('/', careKitController.createCareKit);
router.post('/:id/buy', careKitController.buyCareKit);
router.get('/budget-calculator', careKitController.calculateBudgetKit);

module.exports = router;
