/**
 * Entry Point: POS System REST API Server
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { testConnection } from '../02-Config/db.js';

import authRoutes from '../05-Routes/auth.routes.js';
import franchiseRoutes from '../05-Routes/franchise.routes.js';
import productRoutes from '../05-Routes/product.routes.js';
import billRoutes from '../05-Routes/bill.routes.js';
import { errorHandler } from '../06-Middleware/error.middleware.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

testConnection();

// API Endpoint Mappings
app.use('/api/auth', authRoutes);
app.use('/api/franchises', franchiseRoutes);
app.use('/api/products', productRoutes);
app.use('/api/bills', billRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ success: true, message: 'POS Server is running healthy' });
});

// 404 Route Not Found
app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Route not found' });
});

// Global Error Handler
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`🚀 POS REST API Server running on http://localhost:${PORT}`);
});
