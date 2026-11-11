import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { envConfig } from './config/env.config';
import { apiRoutes } from './routes';
import { errorHandler } from './middleware/error.middleware';
import { standardRateLimiter } from './middleware/rateLimiter.middleware';

import path from 'path';
import { telemetryMiddleware } from './middleware/telemetry.middleware';

export const createApp = (): Express => {
  const app = express();

  // Security headers with CSP relaxed for CDN web control panel
  app.use(
    helmet({
      contentSecurityPolicy: false,
      crossOriginEmbedderPolicy: false
    })
  );

  // CORS configuration
  app.use(
    cors({
      origin: true,
      credentials: true
    })
  );

  // Request logging
  if (envConfig.nodeEnv !== 'test') {
    app.use(morgan('combined'));
  }

  // Body parser
  app.use(express.json({ limit: '5mb' }));
  app.use(express.urlencoded({ extended: true, limit: '5mb' }));

  // Static Assets & Control Panel Web UI
  const publicDir = path.resolve(__dirname, '../public');
  app.use(express.static(publicDir));
  app.use('/public', express.static(publicDir));

  // Direct Web Control Panel endpoints
  app.get(['/', '/control-panel', '/dashboard'], (req, res) => {
    res.sendFile(path.join(publicDir, 'index.html'));
  });

  // Global Rate Limiting
  app.use(standardRateLimiter);

  // Request Telemetry & Real-Time Monitor
  app.use(telemetryMiddleware);

  // API Routes (Mounted on /api/v1, /api, and root /)
  app.use(envConfig.apiPrefix, apiRoutes);
  app.use('/api', apiRoutes);
  app.use('/', apiRoutes);

  // Global Error Handler
  app.use(errorHandler);

  return app;
};
