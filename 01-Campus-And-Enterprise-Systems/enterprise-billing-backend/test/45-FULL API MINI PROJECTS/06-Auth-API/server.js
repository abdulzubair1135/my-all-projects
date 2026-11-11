import express from 'express';
import dotenv from 'dotenv';
import authRoutes from './routes/authRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/auth', authRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'Auth API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 Auth API running on http://localhost:${PORT}`));
