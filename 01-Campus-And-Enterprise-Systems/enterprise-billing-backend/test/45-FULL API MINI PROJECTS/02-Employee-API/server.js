import express from 'express';
import dotenv from 'dotenv';
import employeeRoutes from './routes/employeeRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/employees', employeeRoutes);

app.get('/', (req, res) => res.json({ success: true, message: 'Employee API Ready' }));

app.use(errorHandler);

app.listen(PORT, () => console.log(`🚀 Employee API on http://localhost:${PORT}`));
