/**
 * Entry Point: server.js
 * Express Application initialization and route attachment.
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { testConnection } from './config/db.js';
import userRoutes from './routes/user.routes.js';
import { errorHandler } from './middleware/error.middleware.js';
import { sendSuccess } from './utils/response.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Built-in & Third-Party Middlewares
app.use(cors());
app.use(express.json());

// Database Connection Test
testConnection();

// Health Check Endpoint
app.get('/api/health', (req, res) => {
  return sendSuccess(res, 'CRUD API Service is healthy and running!');
});

// API Routes
app.use('/api/users', userRoutes);

// 404 Route Not Found Handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.originalUrl} not found on this server`
  });
});

// Global Error Handler Middleware (Must be attached last)
app.use(errorHandler);

// Start Server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
