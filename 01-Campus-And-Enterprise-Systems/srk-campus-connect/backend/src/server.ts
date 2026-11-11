import http from 'http';
import { createApp } from './app';
import { connectDatabase } from './config/database';
import { envConfig } from './config/env.config';
import { SocketManager } from './sockets/socket.manager';
import { logger } from './utils/logger';

process.on('uncaughtException', (err) => {
  logger.error('Uncaught Exception:', { err: err.message, stack: err.stack });
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', { promise, reason });
});

const startServer = async () => {
  try {
    // 1. Connect Database
    await connectDatabase();

    // 2. Create Express App
    const app = createApp();

    // 3. Create HTTP Server
    const server = http.createServer(app);

    // 4. Initialize Socket.IO
    SocketManager.initialize(server, envConfig.clientUrls);

    // Keep event loop alive
    setInterval(() => {}, 60000);

    // 5. Start Listening explicitly on 0.0.0.0 (all IPv4 and IPv6 interfaces)
    server.listen(envConfig.port, '0.0.0.0', () => {
      logger.info(`===================================================`);
      logger.info(` Campus Presence & Coordination Platform Backend   `);
      logger.info(` Running in [${envConfig.nodeEnv}] mode on port ${envConfig.port} `);
      logger.info(` API Prefix: ${envConfig.apiPrefix}                    `);
      logger.info(` Health Check: http://localhost:${envConfig.port}${envConfig.apiPrefix}/health`);
      logger.info(`===================================================`);
    });

    const gracefulShutdown = (signal: string) => {
      logger.info(`Received ${signal}. Shutting down gracefully...`);
      server.close(() => {
        logger.info('HTTP server closed.');
        process.exit(0);
      });
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
  } catch (error) {
    logger.error('Failed to bootstrap server', { error });
  }
};

if (process.env.NODE_ENV !== 'test') {
  startServer();
}
