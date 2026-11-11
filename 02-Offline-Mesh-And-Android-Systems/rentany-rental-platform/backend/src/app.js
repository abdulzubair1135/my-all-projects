import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import cookieParser from 'cookie-parser';
import path from 'path';

import { corsOptions, globalLimiter } from './config/security.js';
import { errorHandler, AppError } from './middleware/error.middleware.js';
import routes from './routes/index.js';

const app = express();

// 1. HTTP Security Headers
app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginResourcePolicy: { policy: "cross-origin" } // Allow android client to read static images
}));

// 2. Cross-Origin Resource Sharing
app.use(cors(corsOptions));

// 3. Request Logging
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('dev'));
}

// 4. Rate Limiting protection
app.use(globalLimiter);

// 5. Body Parsers
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// 6. Static Uploads Folder Serving
app.use('/uploads', express.static(path.resolve('uploads')));

// 7. API Routes Registry
app.use('/api', routes);

// Admin panel view route
app.get('/admin', (req, res) => {
  res.sendFile(path.resolve('src/views/admin.html'));
});

// Home Greeting / Health check
app.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'RentAny Production API Server is active and healthy.',
    time: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Comprehensive public API health & service status check
app.get('/api-status', async (req, res) => {
  const { env } = await import('./config/env.js');
  const startTime = Date.now();

  // 1. Database check
  let dbStatus = 'disconnected';
  let dbError = null;
  try {
    const pool = (await import('./config/database.js')).default;
    const connection = await pool.getConnection();
    connection.release();
    dbStatus = 'connected';
  } catch (err) {
    dbError = err.message;
  }

  // 2. Cloudinary check
  let cloudinaryStatus = 'not_configured';
  if (env.CLOUDINARY_CLOUD_NAME && env.CLOUDINARY_API_KEY && env.CLOUDINARY_API_SECRET) {
    cloudinaryStatus = 'configured';
  }

  // 3. Resend check
  let resendStatus = env.RESEND_API_KEY ? 'configured' : 'not_configured';

  // 4. Payment check
  let paymentStatus = env.PAYMENT_SECRET_KEY ? 'configured' : 'not_configured';

  // 5. JWT check
  let jwtStatus = (env.JWT_ACCESS_SECRET && env.JWT_REFRESH_SECRET) ? 'configured' : 'not_configured';

  const allOk = dbStatus === 'connected';

  res.status(allOk ? 200 : 503).json({
    status: allOk ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    responseTime: `${Date.now() - startTime}ms`,
    services: {
      database: {
        status: dbStatus,
        host: env.DB_HOST,
        port: env.DB_PORT,
        name: env.DB_NAME,
        ssl: env.DB_SSL === 'true',
        error: dbError
      },
      cloudinary: {
        status: cloudinaryStatus,
        cloudName: env.CLOUDINARY_CLOUD_NAME || null
      },
      email: {
        status: resendStatus,
        provider: 'Resend',
        fromEmail: env.RESEND_FROM_EMAIL || null
      },
      payments: {
        status: paymentStatus,
        provider: env.PAYMENT_PROVIDER || 'stripe'
      },
      auth: {
        status: jwtStatus,
        accessTokenExpiry: env.JWT_ACCESS_EXPIRES_IN,
        refreshTokenExpiry: env.JWT_REFRESH_EXPIRES_IN
      },
      storage: {
        status: 'local',
        uploadsDir: '/uploads'
      }
    }
  });
});

// Safe database health check (kept for Render probe)
app.get('/health', async (req, res) => {
  let dbStatus = 'healthy';
  try {
    const pool = (await import('./config/database.js')).default;
    const connection = await pool.getConnection();
    connection.release();
  } catch (err) {
    dbStatus = 'unhealthy';
  }
  res.status(dbStatus === 'healthy' ? 200 : 503).json({
    status: dbStatus === 'healthy' ? 'ok' : 'error',
    database: dbStatus === 'healthy' ? 'connected' : 'disconnected'
  });
});

// 8. 404 Route handler
app.use('*', (req, res, next) => {
  next(new AppError(`The requested endpoint (${req.method} ${req.baseUrl}) was not found on this server.`, 404));
});

// 9. Centralized Error Handler
app.use(errorHandler);

// Database Keep-Alive Heartbeat (Run every 10 minutes to prevent Aiven database sleep)
setInterval(async () => {
  try {
    const pool = (await import('./config/database.js')).default;
    await pool.query('SELECT 1');
    console.log('Database keep-alive ping successful:', new Date().toISOString());
  } catch (err) {
    console.error('Database keep-alive ping failed:', err.message);
  }
}, 600000); // 10 minutes

export default app;
