import express from 'express';
import dotenv from 'dotenv';
import productRoutes from './routes/productRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/products', productRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'Product API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 Product API on http://localhost:${PORT}`));
