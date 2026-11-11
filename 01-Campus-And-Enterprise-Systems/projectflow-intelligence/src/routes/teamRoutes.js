const express = require('express');
const router = express.Router();
const teamController = require('../controllers/teamController');

router.get('/team', teamController.getTeamMembers);
router.get('/teams', teamController.getSquadTeams);
router.post('/teams', teamController.createSquadTeam);

module.exports = router;
