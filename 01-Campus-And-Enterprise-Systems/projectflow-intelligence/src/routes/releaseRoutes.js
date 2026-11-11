const express = require('express');
const router = express.Router();
const releaseController = require('../controllers/releaseController');

// Public and Mobile App APK Distribution
router.get('/releases/latest', releaseController.getLatestRelease);
router.get('/releases/:id/download', releaseController.downloadRelease);

// Admin Release Management
router.get('/admin/releases', releaseController.listAdminReleases);
router.post('/admin/releases', releaseController.createRelease);
router.post('/admin/releases/:id/publish', releaseController.publishRelease);
router.post('/admin/releases/:id/unpublish', releaseController.unpublishRelease);

module.exports = router;
