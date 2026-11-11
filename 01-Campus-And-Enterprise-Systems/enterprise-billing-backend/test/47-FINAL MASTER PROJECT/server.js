import express from 'express';
import dotenv from 'dotenv';
import helmet from 'helmet';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

// Route Imports
import authRoutes from './routes/authRoutes.js';
import categoryRoutes from './routes/categoryRoutes.js';
import productRoutes from './routes/productRoutes.js';
import orderRoutes from './routes/orderRoutes.js';

// Middleware Imports
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Set up __dirname equivalent for ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Security Middlewares
app.use(helmet());
app.use(cors());

// Body Parsers
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve Uploaded Media Static Files
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Root Status Check
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: '🚀 Master E-Commerce REST API Server is operational',
    version: '1.0.0',
    documentation: '/docs'
  });
});

// API Routes Registry
app.use('/api/auth', authRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/products', productRoutes);
app.use('/api/orders', orderRoutes);

// Global Error Handler
app.use(errorHandler);

// Start Server
app.listen(PORT, () => {
  console.log(`===================================================`);
  console.log(`🌐 Server running in ${process.env.NODE_ENV || 'development'} mode`);
  console.log(`🚀 Listening at http://localhost:${PORT}`);
  console.log(`===================================================`);
});
