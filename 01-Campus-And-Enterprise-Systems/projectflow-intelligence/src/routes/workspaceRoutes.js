const express = require('express');
const router = express.Router();
const workspaceController = require('../controllers/workspaceController');

router.get('/workspaces', workspaceController.getWorkspaces);
router.post('/workspaces', workspaceController.createWorkspace);
router.get('/workspaces/:id/projects', workspaceController.getWorkspaceProjects);
router.post('/workspaces/:id/projects', workspaceController.createWorkspaceProject);

module.exports = router;
