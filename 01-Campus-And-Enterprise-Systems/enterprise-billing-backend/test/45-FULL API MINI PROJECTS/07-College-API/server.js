import express from 'express';
import dotenv from 'dotenv';
import collegeRoutes from './routes/collegeRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api', collegeRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'College API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 College API on http://localhost:${PORT}`));
