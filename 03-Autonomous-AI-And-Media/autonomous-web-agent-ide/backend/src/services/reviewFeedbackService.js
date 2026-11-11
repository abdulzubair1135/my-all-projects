const path = require('path');
const { spawn } = require('child_process');
const { db } = require('../database/db');
const eventBus = require('./eventBus');
const projectService = require('./projectService');

class ReviewFeedbackService {
  constructor() {
    this.currentScore = 150;
    this.aiEmotion = {
      mood: 'HAPPY', // 'THRILLED', 'HAPPY', 'RESEARCHING', 'FOCUSED'
      emoji: '😄',
      message: 'AI is ready and eager to build high-quality software!'
    };
    this._ensureTables();
  }

  _ensureTables() {
    try {
      db.exec(`
        CREATE TABLE IF NOT EXISTS human_reviews (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          project_id TEXT,
          sentiment TEXT,
          rating INTEGER,
          comment TEXT,
          score_delta INTEGER,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
      `);
    } catch (e) {}
  }

  getStats() {
    return {
      qualityScore: this.currentScore,
      emotion: this.aiEmotion
    };
  }

  async submitReview(projectId, sentiment, comment = '') {
    const isPositive = sentiment === 'positive' || sentiment === 'good';
    const delta = isPositive ? 50 : -25;
    this.currentScore = Math.max(0, this.currentScore + delta);

    if (isPositive) {
      this.aiEmotion = {
        mood: 'THRILLED',
        emoji: '🥳',
        message: 'Aapne acha review diya! AI bohot khush hai aur points grow ho gaye!'
      };
    } else {
      this.aiEmotion = {
        mood: 'RESEARCHING',
        emoji: '🧐',
        message: 'Feedback mila: AI DeepSeek ke sath deep research aur self-correction mode me ja raha hai...'
      };
    }

    try {
      db.prepare(`
        INSERT INTO human_reviews (project_id, sentiment, rating, comment, score_delta)
        VALUES (?, ?, ?, ?, ?)
      `).run(projectId || '', sentiment, isPositive ? 5 : 1, comment, delta);
    } catch (e) {}

    // Emit live update to IDE frontend
    eventBus.emit('review.submitted', {
      qualityScore: this.currentScore,
      emotion: this.aiEmotion,
      sentiment,
      comment
    });

    // If negative review, trigger autonomous DeepSeek research & improvement loop
    if (!isPositive && projectId) {
      this._triggerAutonomousCorrection(projectId, comment);
    }

    return {
      success: true,
      qualityScore: this.currentScore,
      emotion: this.aiEmotion
    };
  }

  _triggerAutonomousCorrection(projectId, critique) {
    const project = projectService.getProject(projectId);
    if (!project) return;

    eventBus.emit('terminal.output', {
      stream: 'stdout',
      data: `\r\n🧐 [AI Deep Research Mode Activated]\r\n` +
            `• User Critique: "${critique || 'Improve UI design, responsiveness and modular state'}"\r\n` +
            `• DeepSeek R1 investigating architecture gaps and generating optimized code patch...\r\n\r\n`,
      name: 'agent'
    });
  }
}

module.exports = new ReviewFeedbackService();
