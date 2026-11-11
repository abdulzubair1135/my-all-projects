const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');

router.get('/tasks', taskController.getAllTasks);
router.post('/tasks', taskController.createTask);
router.patch('/tasks/:id/status', taskController.updateTaskStatus);
router.patch('/tasks/:id', taskController.updateTask);

module.exports = router;
