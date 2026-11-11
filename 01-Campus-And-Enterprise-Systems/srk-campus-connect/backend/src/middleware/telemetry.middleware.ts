import { Request, Response, NextFunction } from 'express';
import { TelemetryService } from '../services/telemetry.service';

export const telemetryMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const start = Date.now();
  const url = req.originalUrl || req.url;

  // Ignore noisy static asset polling
  if (
    url.startsWith('/public') ||
    url.startsWith('/socket.io') ||
    url.endsWith('.png') ||
    url.endsWith('.ico') ||
    url.endsWith('.css') ||
    url.endsWith('.js')
  ) {
    return next();
  }

  res.on('finish', () => {
    const durationMs = Date.now() - start;
    const ip = (req.headers['x-forwarded-for'] as string) || req.socket.remoteAddress || req.ip;
    const userAgent = req.headers['user-agent'] || 'Unknown';

    TelemetryService.logApiRequest({
      method: req.method,
      url,
      status: res.statusCode,
      durationMs,
      ip: typeof ip === 'string' ? ip.split(',')[0].trim() : ip,
      userAgent: typeof userAgent === 'string' ? userAgent.substring(0, 80) : userAgent
    });
  });

  next();
};
