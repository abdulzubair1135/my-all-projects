# SET 08 - Security Best Practices (Helmet, CORS, SQL Injection Prevention)

## Question
Secure an Express.js production API server against common security threats: Cross-Site Scripting (XSS), SQL Injection, CORS vulnerabilities, and header exposure.

---

## Requirements
1. Use `helmet` middleware to set HTTP security headers.
2. Configure `cors` middleware to restrict allowed origins.
3. Enforce prepared statements in `mysql2/promise` to eliminate SQL Injection risk.

---

## Solution Code

### `server.js`
```javascript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';

const app = express();

// Security Headers
app.use(helmet());

// CORS Options
const corsOptions = {
  origin: ['http://localhost:3000', 'https://myfrontend.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

app.use(express.json());

// Prevent SQL Injection using Parameterized Query
app.get('/api/users/search', async (req, res) => {
  const { name } = req.query;
  // SAFE: Parameterized query using ?
  const [rows] = await pool.query('SELECT id, name, email FROM users WHERE name = ?', [name]);
  res.json({ success: true, data: rows });
});
```
