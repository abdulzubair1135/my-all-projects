import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { ResponseUtil } from '../utils/response';

import { TelemetryService } from '../services/telemetry.service';

export const errorHandler = (
  err: any,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  logger.error('Unhandled Server Error', {
    message: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    userId: req.user?._id
  });

  // Track in Telemetry
  try {
    TelemetryService.logError({
      message: err.message || 'Internal Server Error',
      stack: err.stack,
      endpoint: req.originalUrl || req.url,
      method: req.method,
      ip: (req.headers['x-forwarded-for'] as string) || req.socket.remoteAddress || req.ip
    });
  } catch (e) {}

  if (err.name === 'ValidationError') {
    ResponseUtil.error(res, 'Database Validation Failed', 422, err.errors);
    return;
  }

  if (err.code === 11000) {
    ResponseUtil.error(res, 'Duplicate key constraint violation', 409, err.keyValue);
    return;
  }

  const statusCode = err.statusCode || 500;
  const message = process.env.NODE_ENV === 'production' && statusCode === 500
    ? 'Internal server error occurred'
    : err.message || 'Internal server error';

  ResponseUtil.error(res, message, statusCode);
};
