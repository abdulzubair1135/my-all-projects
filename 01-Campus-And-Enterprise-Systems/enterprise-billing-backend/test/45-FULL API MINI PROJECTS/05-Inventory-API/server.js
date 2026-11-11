import express from 'express';
import dotenv from 'dotenv';
import inventoryRoutes from './routes/inventoryRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/inventory', inventoryRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'Inventory API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 Inventory API on http://localhost:${PORT}`));
