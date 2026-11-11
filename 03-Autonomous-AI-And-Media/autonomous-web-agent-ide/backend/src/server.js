require('dotenv').config();
const http = require('http');
const express = require('express');
const cors = require('cors');
const path = require('path');
const { db } = require('./database/db');
const apiRoutes = require('./routes/api');
const { initWebSocketServer } = require('./websocket/ws');
const processManager = require('./services/processManager');

const app = express();
const server = http.createServer(app);

// Middleware
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// REST Routes
app.use('/api', apiRoutes);

// Static Workspace Serve (for web runners, generated assets, live HTML previews)
app.use('/workspace', express.static(path.join(__dirname, '../../workspace')));

// Initialize WebSocket server
initWebSocketServer(server);

// Global Error Handler
app.use((err, req, res, next) => {
  console.error('Express Unhandled Error:', err);
  res.status(500).json({ error: err.message || 'Internal Server Error' });
});

const PORT = process.env.BACKEND_PORT || 3001;

async function start() {
  await db.ready;
  server.listen(PORT, () => {
    console.log(`[Autonomous Web-Agent IDE Backend] listening on http://localhost:${PORT}`);
    console.log(`[WebSocket Server] active at ws://localhost:${PORT}/ws`);
  });
}

start();

// Graceful Shutdown
function handleShutdown(signal) {
  console.log(`\nReceived ${signal}, shutting down gracefully...`);
  processManager.cleanupAll();
  server.close(() => {
    console.log('Backend server closed cleanly.');
    process.exit(0);
  });
}

process.on('SIGINT', () => handleShutdown('SIGINT'));
process.on('SIGTERM', () => handleShutdown('SIGTERM'));

module.exports = { app, server };
