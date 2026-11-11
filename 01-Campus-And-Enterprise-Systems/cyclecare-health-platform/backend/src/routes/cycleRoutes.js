const express = require('express');
const router = express.Router();
const cycleController = require('../controllers/cycleController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', cycleController.getCycleData);
router.post('/', cycleController.addPeriodLog);
router.put('/:id', cycleController.updatePeriodLog);
router.delete('/:id', cycleController.deletePeriodLog);
router.get('/history', cycleController.getCycleHistory);
router.get('/prediction', cycleController.getPrediction);
router.get('/insights', cycleController.getInsights);

// Aliases for Android client backward compatibility
router.post('/period', cycleController.addPeriodLog);
router.patch('/period/:id', cycleController.updatePeriodLog);
router.delete('/period/:id', cycleController.deletePeriodLog);

module.exports = router;
