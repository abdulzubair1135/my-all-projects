const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const settingsController = require('../controllers/settingsController');
const telemetryController = require('../controllers/telemetryController');

// Overview Metrics
router.get('/admin/overview', settingsController.getAdminOverview);

// User RBAC Management
router.get('/admin/users', adminController.getAdminUsers);
router.post('/admin/users', adminController.inviteUser);
router.patch('/admin/users/:id/role', adminController.updateUserRole);
router.patch('/admin/users/:id/status', adminController.toggleUserStatus);

// Workspaces & Projects Listing for Admin
router.get('/admin/workspaces', adminController.getAdminWorkspaces);
router.get('/admin/projects', adminController.getAdminProjects);

// System Health & Error Probes
router.get('/admin/system/health', telemetryController.getSystemHealth);
router.get('/admin/system/errors', telemetryController.getSystemErrors);
router.patch('/admin/system/errors/:id/resolve', telemetryController.resolveSystemError);

// Audit Events
router.get('/admin/audit-events', telemetryController.getAuditLogs);

// System Settings
router.get('/admin/settings', settingsController.getSettings);
router.patch('/admin/settings', settingsController.updateSettings);

// Reports & Real-Time Analytics
router.get('/reports/summary', settingsController.getReportsSummary);

module.exports = router;
