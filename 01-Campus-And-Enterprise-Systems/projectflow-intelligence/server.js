require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { store } = require('./src/supabase');
const { presenceAndAuthMiddleware } = require('./src/middleware/authMiddleware');

// Modular Route Controllers
const authRoutes = require('./src/routes/authRoutes');
const workspaceRoutes = require('./src/routes/workspaceRoutes');
const projectRoutes = require('./src/routes/projectRoutes');
const taskRoutes = require('./src/routes/taskRoutes');
const teamRoutes = require('./src/routes/teamRoutes');
const chatRoutes = require('./src/routes/chatRoutes');
const notificationRoutes = require('./src/routes/notificationRoutes');
const riskRoutes = require('./src/routes/riskRoutes');
const releaseRoutes = require('./src/routes/releaseRoutes');
const adminRoutes = require('./src/routes/adminRoutes');
const telemetryRoutes = require('./src/routes/telemetryRoutes');

const app = express();
const PORT = process.env.PORT || 8082;

// Core Middleware
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use(presenceAndAuthMiddleware);

// Serve static assets
app.use(express.static(path.join(__dirname, 'admin-panel', 'public')));
app.use(express.static(path.join(__dirname, 'admin-panel', 'dist')));
app.use('/releases', express.static(path.join(__dirname, 'releases')));

// System Settings Defaults
store.settings = store.settings || {
  syncIntervalMinutes: 15,
  maxBatchSize: 100,
  offlineGracePeriodHours: 72,
  fcmEnabled: true,
  fcmSenderId: '768921827461',
  organizationName: 'ProjectFlow Enterprise',
  contactEmail: 'admin@projectflow.io',
  riskSeverityThreshold: 'MEDIUM',
  updatedAt: new Date().toISOString()
};

// Mount API Routers
app.use('/api/v1', authRoutes);
app.use('/api/v1', workspaceRoutes);
app.use('/api/v1', projectRoutes);
app.use('/api/v1', taskRoutes);
app.use('/api/v1', teamRoutes);
app.use('/api/v1', chatRoutes);
app.use('/api/v1', notificationRoutes);
app.use('/api/v1', riskRoutes);
app.use('/api/v1', releaseRoutes);
app.use('/api/v1', adminRoutes);
app.use('/api/v1', telemetryRoutes);

// SPA Frontend Fallback (Serves Admin Panel on root and all client routes)
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, 'admin-panel', 'dist', 'index.html');
  res.sendFile(indexPath, (err) => {
    if (err) {
      res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>ProjectFlow Intelligence</title></head>
        <body style="font-family:sans-serif;background:#F4F2E9;color:#292D28;padding:40px;text-align:center;">
          <h1>ProjectFlow Intelligence API is Operational</h1>
          <p>REST API running at <a href="/api/v1/admin/overview">/api/v1/admin/overview</a></p>
        </body>
        </html>
      `);
    }
  });
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`[PROJECTFLOW] JavaScript Backend listening on port ${PORT}`);
});

module.exports = { app, server };
