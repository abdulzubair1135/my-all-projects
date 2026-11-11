import express from 'express';
import dotenv from 'dotenv';
import studentRoutes from './routes/studentRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Body Parser Middleware
app.use(express.json());

// API Routes
app.use('/api/students', studentRoutes);

// Root Route
app.get('/', (req, res) => {
  res.json({ success: true, message: 'Student API is running smoothly!' });
});

// Global Error Middleware
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`🚀 Student API running on http://localhost:${PORT}`);
});
