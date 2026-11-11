const express = require('express');
const router = express.Router();
const symptomsController = require('../controllers/symptomsController');
const authenticateToken = require('../middleware/auth');

router.use(authenticateToken);

router.get('/', symptomsController.getSymptoms);
router.post('/log', symptomsController.logSymptom);
router.get('/history', symptomsController.getSymptomHistory);
router.delete('/log/:id', symptomsController.deleteSymptomLog);

module.exports = router;
