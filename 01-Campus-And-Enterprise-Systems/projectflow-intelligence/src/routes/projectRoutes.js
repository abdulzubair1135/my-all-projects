const express = require('express');
const router = express.Router();
const projectController = require('../controllers/projectController');
const workspaceController = require('../controllers/workspaceController');
const taskController = require('../controllers/taskController');
const riskController = require('../controllers/riskController');

// Projects CRUD & Details
router.get('/projects', projectController.getAllProjects);
router.post('/projects', workspaceController.createWorkspaceProject);
router.patch('/projects/:id', projectController.updateProject);

// Project Tasks
router.get('/projects/:id/tasks', taskController.getProjectTasks);
router.post('/projects/:id/tasks', taskController.createTask);

// Project Risk Radar & Scenario Evaluation
router.get('/projects/:id/risks', riskController.getProjectRisks);
router.post('/projects/:id/risks/evaluate', riskController.evaluateRisks);
router.post('/projects/:id/scenarios/evaluate', riskController.evaluateProjectScenario);

module.exports = router;
