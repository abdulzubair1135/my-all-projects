const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const config = require('./config/config');
const logger = require('./utils/logger');
const { getDatabase, closeDatabase } = require('./database/database');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

const { securityHardening } = require('./middleware/securityHardening');

// Global active tunnel URL — updated whenever Cloudflare tunnel connects
global.activeTunnelUrl = null;

// Initialize Database and Schema on startup
getDatabase();

const app = express();

// Apply Security Hardening & Headers
app.use(securityHardening);

// Bypass Localtunnel reminder page for API requests
app.use((req, res, next) => {
  res.setHeader('bypass-tunnel-reminder', 'true');
  next();
});

// Disable x-powered-by and apply security headers with font & inline script permissions
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:"]
    }
  }
}));

// Trust proxy for LAN/Tailscale reverse proxy if ever placed behind one
app.set('trust proxy', 1);

// General rate limiter
const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 600, // 600 requests per minute
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: 'Too many requests, please try again later.'
  }
});
app.use(generalLimiter);

// Parse JSON bodies — 2GB limit for large file backup chunks
app.use(express.json({ limit: '2gb' }));
app.use(express.urlencoded({ extended: true, limit: '2gb' }));

// Set 30-minute timeout for large file uploads
app.use((req, res, next) => {
  req.setTimeout(30 * 60 * 1000); // 30 minutes
  res.setTimeout(30 * 60 * 1000);
  next();
});

// Logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (res.statusCode >= 400) {
      logger.warn('HTTP', `${req.method} ${req.originalUrl} ${res.statusCode} (${duration}ms)`, {
        ip: req.ip,
        status: res.statusCode
      });
    }
  });
  next();
});

const path = require('path');

// Import route modules
const healthRouter = require('./routes/health');
const deviceRouter = require('./routes/device');
const syncRouter = require('./routes/sync');
const vaultRouter = require('./routes/vault');
const webRouter = require('./routes/web');

// Serve Web Management Dashboard static assets
app.use(express.static(path.join(__dirname, 'public')));

// Mount routes
app.use('/api/health', healthRouter);
app.use('/api/device', deviceRouter);
app.use('/api/sync', syncRouter);
app.use('/api/vault', vaultRouter);
app.use('/api/web', webRouter);

// Tunnel URL discovery endpoint — App calls this on startup to get latest tunnel URL
app.get('/api/tunnel-url', (req, res) => {
  res.json({
    success: true,
    tunnel_url: global.activeTunnelUrl || null,
    local_ip: '10.221.241.31',
    port: 8088
  });
});
// Direct APK download endpoint for the user's phone
app.get('/download', (req, res) => {
  const apkPath = 'C:\\Vault\\PersonalLifeVault.apk';
  const fs = require('fs');
  if (fs.existsSync(apkPath)) {
    res.download(apkPath, 'PersonalLifeVault.apk');
  } else {
    res.status(404).send('APK build not found');
  }
});

// Shortcut route for /api/storage pointing to vaultRouter's storage handler
app.use('/api/storage', (req, res, next) => {
  req.url = '/storage';
  vaultRouter(req, res, next);
});

// 404 and global error handling
app.use(notFoundHandler);
app.use(errorHandler);

// Start server
const server = app.listen(config.port, config.host, () => {
  logger.info('SERVER', `Personal Life Vault Server listening on http://${config.host}:${config.port}`);
  logger.info('SERVER', `Vault storage location: ${config.storageRoot}`);
  logger.info('SERVER', `Database location: ${config.databasePath}`);
  startPermanentTunnel();
});

// Auto-launcher for Permanent Ngrok Tunnel
const { exec, spawn } = require('child_process');
let ngrokProc = null;

function startPermanentTunnel() {
  if (process.env.RENDER || process.platform !== 'win32') {
    logger.info('TUNNEL', 'Running on cloud/Render environment. Local Ngrok tunnel bypassed.');
    return;
  }
  logger.info('TUNNEL', '🚀 Launching Permanent Ngrok Tunnel & ADB Reverse...');
  try {
    // 1. Auto-setup ADB Reverse Tunnel for 0ms USB connection fallback
    exec('C:\\Users\\abdul\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe reverse tcp:8088 tcp:8088', () => {});

    if (ngrokProc) {
      try { ngrokProc.kill(); } catch (_) {}
      ngrokProc = null;
    }

    // 2. Start Ngrok with PERMANENT domain: illusion-roundish-configure.ngrok-free.dev
    ngrokProc = spawn('C:\\Vault\\ngrok.exe', [
      'http',
      '8088',
      '--domain=illusion-roundish-configure.ngrok-free.dev'
    ], {
      shell: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    global.activeTunnelUrl = 'https://illusion-roundish-configure.ngrok-free.dev';
    logger.info('TUNNEL', '✅ NGROK PERMANENT TUNNEL LIVE: https://illusion-roundish-configure.ngrok-free.dev');

    ngrokProc.on('close', (code) => {
      logger.warn('TUNNEL', `Ngrok process exited (code=${code}) — restarting in 5s...`);
      setTimeout(startPermanentTunnel, 5000);
    });
  } catch (e) {
    logger.error('TUNNEL', `Failed to launch ngrok tunnel: ${e.message}`);
  }
}


// Graceful shutdown handling
function handleShutdown(signal) {
  logger.info('SERVER', `Received ${signal}. Shutting down gracefully...`);
  server.close(() => {
    logger.info('SERVER', 'HTTP server closed.');
    closeDatabase();
    process.exit(0);
  });

  // Force close if lingering
  setTimeout(() => {
    logger.error('SERVER', 'Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 5000);
}

process.on('SIGINT', () => handleShutdown('SIGINT'));
process.on('SIGTERM', () => handleShutdown('SIGTERM'));

module.exports = { app, server };
