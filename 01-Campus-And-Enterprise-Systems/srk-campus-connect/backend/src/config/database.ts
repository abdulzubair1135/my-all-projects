import mongoose from 'mongoose';
import dns from 'dns';
import { envConfig } from './env.config';
import { logger } from '../utils/logger';

// Ensure SRV records resolve cleanly on Windows network adapters
try {
  dns.setServers(['8.8.8.8', '1.1.1.1', '8.8.4.4']);
} catch (e) {
  // fallback to system resolver if restricted
}

export const connectDatabase = async (customUri?: string): Promise<typeof mongoose> => {
  const uri = customUri || (envConfig.nodeEnv === 'test' ? envConfig.mongodbTestUri : envConfig.mongodbUri);
  try {
    const conn = await mongoose.connect(uri, {
      autoIndex: true,
      serverSelectionTimeoutMS: 15000,
      connectTimeoutMS: 15000
    });
    logger.info(`MongoDB Connected successfully to: ${conn.connection.host}/${conn.connection.name}`);
    return conn;
  } catch (error) {
    logger.error('Failed to connect to MongoDB', { error });
    throw error;
  }
};

export const disconnectDatabase = async (): Promise<void> => {
  try {
    await mongoose.disconnect();
    logger.info('MongoDB disconnected cleanly');
  } catch (error) {
    logger.error('Error disconnecting MongoDB', { error });
  }
};
