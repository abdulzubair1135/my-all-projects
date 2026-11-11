import rateLimit from 'express-rate-limit';
import { env } from './env.js';

// Secure CORS options resolving origin checks
export const corsOptions = {
  origin: (origin, callback) => {
    // Mobile apps, Postman, and curl requests typically do not send an Origin header
    if (!origin) {
      return callback(null, true);
    }

    if (env.CORS_ORIGINS === '*') {
      if (env.NODE_ENV === 'production') {
        // In production, reject wildcards for credentials safety
        return callback(new Error('Insecure wildcard CORS not allowed in production with credentials.'), false);
      }
      return callback(null, true);
    }

    const whitelist = env.CORS_ORIGINS.split(',').map(o => o.trim());
    if (whitelist.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error(`Origin ${origin} not allowed by CORS policy.`), false);
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
};

// Global rate limiter (150 requests per 15 minutes)
export const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // Limit each IP to 200 requests per window
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    message: 'Too many requests from this IP, please try again after 15 minutes'
  }
});

// Authentication rate limiter (15 requests per 15 minutes)
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 15,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    message: 'Too many login attempts from this IP, please try again after 15 minutes'
  }
});
