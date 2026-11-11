const express = require('express');
const router = express.Router();
const wellnessController = require('../controllers/wellnessController');

router.get('/articles', wellnessController.getArticles);
router.get('/articles/:id', wellnessController.getArticleById);
router.get('/categories', wellnessController.getCategories);

module.exports = router;
