const express = require('express');
const router = express.Router();
const telemetryController = require('../controllers/telemetryController');

router.post('/telemetry/errors', telemetryController.logClientError);

module.exports = router;
