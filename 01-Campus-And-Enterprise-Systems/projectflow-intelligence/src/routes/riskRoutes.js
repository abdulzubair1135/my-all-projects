const express = require('express');
const router = express.Router();
const riskController = require('../controllers/riskController');

router.post('/scenarios/simulate', riskController.simulateScenario);

module.exports = router;
