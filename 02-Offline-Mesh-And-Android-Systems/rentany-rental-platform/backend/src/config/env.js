import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load env variables from the root .env
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

export const env = {
  PORT: Number(process.env.PORT) || 5000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // Database configurations
  DB_HOST: process.env.DB_HOST || 'localhost',
  DB_PORT: Number(process.env.DB_PORT) || 3306,
  DB_USER: process.env.DB_USER || 'root',
  DB_PASSWORD: process.env.DB_PASSWORD || '',
  DB_NAME: process.env.DB_NAME || 'rentany',
  DB_SSL: process.env.DB_SSL || 'false',
  DB_SSL_CA: process.env.DB_SSL_CA || '',
  
  // JWT tokens secrets
  JWT_ACCESS_SECRET: process.env.JWT_ACCESS_SECRET || 'jwt_access_secret_fallback_12345',
  JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET || 'jwt_refresh_secret_fallback_54321',
  JWT_ACCESS_EXPIRES_IN: process.env.JWT_ACCESS_EXPIRES_IN || '15m',
  JWT_REFRESH_EXPIRES_IN: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
  
  // CORS & Security configs
  CORS_ORIGINS: process.env.CORS_ORIGINS || process.env.CORS_ORIGIN || '*',
  UPLOAD_MAX_SIZE: Number(process.env.UPLOAD_MAX_SIZE) || 5 * 1024 * 1024,
  
  // Payments
  PAYMENT_PROVIDER: process.env.PAYMENT_PROVIDER || 'stripe',
  PAYMENT_SECRET_KEY: process.env.PAYMENT_SECRET_KEY || 'sk_test_mock',

  // Cloudinary
  CLOUDINARY_CLOUD_NAME: process.env.CLOUDINARY_CLOUD_NAME,
  CLOUDINARY_API_KEY: process.env.CLOUDINARY_API_KEY,
  CLOUDINARY_API_SECRET: process.env.CLOUDINARY_API_SECRET,

  // Resend
  RESEND_API_KEY: process.env.RESEND_API_KEY,
  RESEND_FROM_EMAIL: process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev'
};
