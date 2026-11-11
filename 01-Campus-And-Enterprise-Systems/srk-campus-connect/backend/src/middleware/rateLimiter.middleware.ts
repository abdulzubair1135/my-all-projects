import { Request, Response, NextFunction } from 'express';
import rateLimit from 'express-rate-limit';
import { envConfig } from '../config/env.config';
import { ResponseUtil } from '../utils/response';

// Pass-through middleware for test environment
const noopMiddleware = (req: Request, res: Response, next: NextFunction) => next();

export const standardRateLimiter = envConfig.nodeEnv === 'test'
  ? noopMiddleware
  : rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 2000,
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req, res) => {
        ResponseUtil.error(res, 'Too many requests, please try again later.', 429);
      }
    });

export const authRateLimiter = envConfig.nodeEnv === 'test'
  ? noopMiddleware
  : rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 20,
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req, res) => {
        ResponseUtil.error(res, 'Too many authentication attempts, please try again in 15 minutes.', 429);
      }
    });

export const syncRateLimiter = envConfig.nodeEnv === 'test'
  ? noopMiddleware
  : rateLimit({
      windowMs: 5 * 60 * 1000,
      max: envConfig.syncRateLimitMaxRequests,
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req, res) => {
        ResponseUtil.error(res, 'Too many sync requests, rate limit exceeded.', 429);
      }
    });
