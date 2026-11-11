import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });
dotenv.config({ path: path.resolve(__dirname, '../../.env') });
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

export const envConfig = {
  port: parseInt(process.env.PORT || '5001', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  apiPrefix: process.env.API_PREFIX || '/api/v1',
  clientUrls: (process.env.CLIENT_URL || 'http://localhost:3000,http://localhost:8080').split(','),
  
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/campus_coordination_db',
  mongodbTestUri: process.env.MONGODB_TEST_URI || 'mongodb://localhost:27017/campus_coordination_test_db',
  
  jwtSecret: process.env.JWT_SECRET || 'super_secret_access_jwt_key_campus_presence_2026_change_in_prod',
  jwtRefreshSecret: process.env.JWT_REFRESH_SECRET || 'super_secret_refresh_jwt_key_campus_presence_2026_change_in_prod',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '15m',
  jwtRefreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d',
  
  qrHmacSecret: process.env.QR_HMAC_SECRET || 'super_secret_qr_hmac_signing_key_2026_change_in_prod',
  qrNonceTtlSeconds: parseInt(process.env.QR_NONCE_TTL_SECONDS || '30', 10),
  
  rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
  rateLimitMaxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
  syncRateLimitMaxRequests: parseInt(process.env.SYNC_RATE_LIMIT_MAX_REQUESTS || '300', 10)
};
