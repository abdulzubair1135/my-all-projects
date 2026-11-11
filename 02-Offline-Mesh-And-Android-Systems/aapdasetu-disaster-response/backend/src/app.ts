import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';

import authRoutes from './routes/auth.js';
import sosRoutes from './routes/sos.js';
import syncRoutes from './routes/sync.js';
import alertRoutes from './routes/alerts.js';
import hospitalRoutes from './routes/hospitals.js';
import shelterRoutes from './routes/shelters.js';
import rescueTeamRoutes from './routes/rescueTeams.js';
import reportRoutes from './routes/reports.js';
import volunteerRoutes from './routes/volunteers.js';
import ngoRoutes from './routes/ngos.js';
import resourceRoutes from './routes/resources.js';
import adminRoutes from './routes/admin.js';
import uploadRoutes from './routes/upload.js';
import directiveRoutes from './routes/directives.js';
import path from 'path';

const app = express();

app.use(cors({ origin: '*' }));
app.use(helmet({ contentSecurityPolicy: false, crossOriginResourcePolicy: { policy: "cross-origin" } }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(morgan('dev'));

// Static uploads serving
app.use('/uploads', express.static(path.join(process.cwd(), 'uploads')));

// Root status & health checks
app.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'online',
    system: 'Sahay Disaster Command & Emergency Mesh API',
    tagline: "When the Network Fails, Sahay Doesn't.",
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      health: '/api/health',
      auth: '/api/auth',
      sos: '/api/sos',
      reports: '/api/reports',
      alerts: '/api/alerts'
    }
  });
});

app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'online',
    system: 'AapdaSetu Real-Time Emergency Engine',
    timestamp: new Date().toISOString()
  });
});

// Mount routes
app.use('/api/auth', authRoutes);
app.use('/api/sos', sosRoutes);
app.use('/api', syncRoutes); // provides /api/sync & /api/relay
app.use('/api/alerts', alertRoutes);
app.use('/api/hospitals', hospitalRoutes);
app.use('/api/shelters', shelterRoutes);
app.use('/api/rescue-teams', rescueTeamRoutes);
app.use('/api/reports', reportRoutes);
app.use('/api/volunteers', volunteerRoutes);
app.use('/api/ngos', ngoRoutes);
app.use('/api/resources', resourceRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/upload', uploadRoutes);
app.use('/api/directives', directiveRoutes);

// 404 Handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: { code: 'NOT_FOUND', message: `Route not found: ${req.method} ${req.originalUrl}` }
  });
});

// Global Error Handler
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error('[Error] Unhandled exception:', err);
  res.status(err.status || 500).json({
    success: false,
    error: {
      code: err.code || 'INTERNAL_SERVER_ERROR',
      message: err.message || 'An unexpected error occurred.'
    }
  });
});

export default app;
