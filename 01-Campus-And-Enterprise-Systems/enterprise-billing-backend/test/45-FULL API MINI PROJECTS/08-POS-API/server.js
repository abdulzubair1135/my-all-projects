import express from 'express';
import dotenv from 'dotenv';
import posRoutes from './routes/posRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/pos', posRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'POS API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 POS API running on http://localhost:${PORT}`));
