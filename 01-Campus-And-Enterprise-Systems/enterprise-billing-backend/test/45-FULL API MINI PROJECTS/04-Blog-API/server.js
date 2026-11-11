import express from 'express';
import dotenv from 'dotenv';
import postRoutes from './routes/postRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/posts', postRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'Blog API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 Blog API on http://localhost:${PORT}`));
